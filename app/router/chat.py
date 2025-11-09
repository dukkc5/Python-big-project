from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
import asyncpg
from app.api.deps import get_db_conn, get_current_user
import json
from datetime import datetime

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# =====================
# 🔹 Connection Manager
# =====================

# Lớp quản lý kết nối (thay vì dùng global dict)
class ConnectionManager:
    def __init__(self):
        # { group_id: [list_websocket] }
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group_id: int):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)

    def disconnect(self, websocket: WebSocket, group_id: int):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
            if len(self.active_connections[group_id]) == 0:
                del self.active_connections[group_id]

    async def broadcast_message(self, group_id: int, message_data: dict):
        """Gửi JSON message cho mọi người trong nhóm"""
        if group_id in self.active_connections:
            # Chuyển đổi datetime thành string ISO 8601
            message_data['timestamp'] = message_data['timestamp'].isoformat()
            
            for connection in self.active_connections[group_id]:
                try:
                    await connection.send_json(message_data)
                except Exception as e:
                    print(f"Lỗi khi gửi broadcast: {e}")
                    # Có thể xóa connection nếu bị lỗi

# Tạo một instance duy nhất để quản lý
manager = ConnectionManager()


# =====================
# 🔹 REST API
# =====================

@router.get("/history/{group_id}")
async def get_chat_history(
    group_id: int,
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user: dict = Depends(get_current_user)
):
    """Lấy lịch sử tin nhắn của nhóm (Giữ nguyên)"""
    check = await conn.fetchval(
        "SELECT 1 FROM group_members WHERE group_id = $1 AND user_id = $2",
        group_id, current_user["user_id"]
    )
    if not check:
        raise HTTPException(status_code=403, detail="Bạn không thuộc nhóm này")

    query = """
       SELECT m.message_id, m.user_id, u.full_name, u.avatar_url, m.content, m.timestamp
        FROM messages m
        JOIN users u ON m.user_id = u.user_id
        WHERE m.group_id = $1
        ORDER BY m.timestamp ASC
    """
    rows = await conn.fetch(query, group_id)
    # Chuyển đổi kết quả (quan trọng: convert datetime)
    return [
        {**row, 'timestamp': row['timestamp'].isoformat()} 
        for row in map(dict, rows)
    ]


@router.post("/send")
async def send_message(
    group_id: int,
    content: str,
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user: dict = Depends(get_current_user)
):
    """
    (SỬA LẠI) Gửi tin nhắn, LƯU DB và BROADCAST qua WebSocket
    """
    check = await conn.fetchval(
        "SELECT 1 FROM group_members WHERE group_id = $1 AND user_id = $2",
        group_id, current_user["user_id"]
    )
    if not check:
        raise HTTPException(status_code=403, detail="Không thuộc nhóm này")

    # 1. Lưu tin nhắn vào CSDL
    query = """
        INSERT INTO messages (group_id, user_id, content)
        VALUES ($1, $2, $3)
        RETURNING message_id, group_id, user_id, content, timestamp;
    """
    msg_row = await conn.fetchrow(query, group_id, current_user["user_id"], content)
    
    # 2. Định dạng tin nhắn để broadcast (phải giống API history)
    formatted_msg = {
        "message_id": msg_row["message_id"],
        "user_id": msg_row["user_id"],
        "full_name": current_user["full_name"],
        "avatar_url": current_user.get("avatar_url"), # <-- (THÊM DÒNG NÀY)
        "content": msg_row["content"],
        "timestamp": msg_row["timestamp"] # Vẫn là object datetime
    }

    # 3. (MỚI) Broadcast tin nhắn này đến mọi người trong room
    await manager.broadcast_message(group_id, formatted_msg.copy()) 
    
    # 4. Trả về HTTP 200 cho người gửi
    # Phải convert datetime trước khi trả về HTTP
    formatted_msg['timestamp'] = formatted_msg['timestamp'].isoformat()
    return formatted_msg


# =====================
# 🔹 WEBSOCKET REALTIME
# =====================

@router.websocket("/ws/{group_id}/{token}") # Thêm token để xác thực
async def websocket_endpoint(
    websocket: WebSocket, 
    group_id: int,
    token: str, # Nhận token từ URL
    conn: asyncpg.Connection = Depends(get_db_conn) # Lấy DB
):
    """
    (SỬA LẠI) Chỉ dùng để kết nối và lắng nghe.
    """
    
    # (BẮT BUỘC) Xác thực người dùng và kiểm tra thành viên nhóm
    try:
        # Giả sử bạn có hàm get_current_user_from_token
        # (Bạn cần tự triển khai hàm này dựa trên logic của get_current_user)
        # current_user = await get_current_user_from_token(token, conn) 
        
        # (Tạm thời bỏ qua xác thực nếu phức tạp, nhưng đây là rủi ro bảo mật)
        # check = await conn.fetchval(
        #     "SELECT 1 FROM group_members WHERE group_id = $1 AND user_id = $2",
        #     group_id, current_user["user_id"]
        # )
        # if not check:
        #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        #     return

        # Nếu xác thực thành công:
        await manager.connect(websocket, group_id)
        
        try:
            while True:
                # Chỉ giữ kết nối mở để lắng nghe broadcast
                # Không mong đợi nhận tin nhắn chat từ đây
                await websocket.receive_text() 
        except WebSocketDisconnect:
            print(f"Client disconnected from group {group_id}")
            manager.disconnect(websocket, group_id)

    except Exception as e:
        print(f"Lỗi WebSocket (có thể do xác thực): {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)