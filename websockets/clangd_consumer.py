# myproj/clangd_consumer.py
import logging
import asyncio
import os
from channels.generic.websocket import AsyncWebsocketConsumer

# ---- LSP helpers: frame/unframe stdio messages -----------------------------

logger = logging.getLogger('obi')

def lsp_frame(json_bytes: bytes) -> bytes:
    # LSP transport: "Content-Length: N\r\n\r\n<json>"
    return b"Content-Length: " + str(len(json_bytes)).encode() + b"\r\n\r\n" + json_bytes

async def lsp_read_message(stream: asyncio.StreamReader) -> bytes:
    """
    Read one LSP message from clangd stdout: parse headers to get Content-Length,
    then read that many bytes of the JSON body. Return the body only.
    """
    # read headers
    headers = b""
    while b"\r\n\r\n" not in headers:
        chunk = await stream.readuntil(b"\r\n")
        headers += chunk
        # guard against absurd header growth
        if len(headers) > 32 * 1024:
            raise RuntimeError("LSP header too large")

    head, _sep, _rest = headers.partition(b"\r\n\r\n")
    content_length = None
    for line in head.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            content_length = int(line.split(b":", 1)[1].strip())
            break
    if content_length is None:
        raise RuntimeError("No Content-Length in LSP headers")

    # read body
    body = await stream.readexactly(content_length)
    return body

# ---- Consumer ---------------------------------------------------------------


class ClangdConsumer(AsyncWebsocketConsumer):
    """
    Bridges WS <-> clangd (stdio LSP).
    Client side sends/receives plain JSON-RPC frames over WebSocket.
    We add/remove LSP Content-Length framing for clangd.
    """

    compile_commands_json = r'''[
    {
    "directory": "/home/olimpinf/clangd_workspaces/%(user_id)s",
    "command": "/usr/bin/clang++ -std=c++20 -I/home/olimpinf/clangd_workspaces/default -I/usr/include/c++/13 -I/usr/include/x86_64-linux-gnu/c++/13 -I/usr/include/c++/13/backward -I/usr/lib/gcc/x86_64-linux-gnu/13/include -I/usr/local/include -I/usr/include/x86_64-linux-gnu -I/usr/include /home/olimpinf/clangd_workspaces/%(user_id)s/main.cpp",
    "file": "/home/olimpinf/clangd_workspaces/%(user_id)s/main.cpp"
    }
]
'''
    
    async def connect(self):
        await self.accept()

        # workspace directory containing (or resolving to) compile_commands.json
        # you can pick per-user/project via URL querystring, cookies, auth, etc.

        # Get authenticated student from Django user
        # logger.info("connect")

        logger.info("connect")

        try:
            student_id = self.scope['user'].id if self.scope['user'].is_authenticated else 'anonymous'
        except:
            student_id = 'none'
        logger.info(f"student_id={student_id}")
        
        try:
            user_id = self.scope['user'].id
        except:
            user_id = '00000-A'
        if not user_id:
            logger.info("no user")
            await self.close(code=4001)  # Unauthorized
            return
    
        # Per-student workspace
        base_workspace = "/home/olimpinf/clangd_workspaces"
        self.workspace = os.path.join(base_workspace, str(user_id))
        os.makedirs(self.workspace, exist_ok=True)

        main_cpp = os.path.join(self.workspace, "main.cpp")
        if not os.path.exists(main_cpp):
            with open(main_cpp, 'w') as f:
                f.write("// Digite seu código aqui\n")

        self.compile_commands_file = os.path.join(self.workspace, "compile_commands.json")
        with open(self.compile_commands_file, 'w') as f:
            f.write(self.compile_commands_json % {'user_id': user_id})

        self.clangd_cmd = os.environ.get("CLANGD_CMD", "clangd")

        # start clangd
        self.proc = await asyncio.create_subprocess_exec(
            self.clangd_cmd,
            "--enable-config",
            "--background-index",
            "--clang-tidy",
            "--header-insertion=never",
            f"--compile-commands-dir={self.workspace}",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.workspace,
        )

        # task to pump clangd → WS
        self.to_ws = asyncio.create_task(self._pump_to_ws())

        # optional: log stderr (helpful during setup)
        self.stderr_task = asyncio.create_task(self._log_stderr())

    async def disconnect(self, code):
        try:
            if self.to_ws: self.to_ws.cancel()
            if self.stderr_task: self.stderr_task.cancel()
            if self.proc and self.proc.returncode is None:
                self.proc.kill()
        except Exception:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        """
        From browser → we receive a JSON-RPC frame (string).
        Wrap with LSP headers and write to clangd stdin.
        """
        if not self.proc or not self.proc.stdin:
            return
        data = None
        if text_data is not None:
            data = text_data.encode("utf-8")
        elif bytes_data is not None:
            data = bytes_data
        if data is None:
            return

        try:
            self.proc.stdin.write(lsp_frame(data))
            await self.proc.stdin.drain()
        except (BrokenPipeError, ConnectionResetError):
            await self.close(code=1011)

    async def _pump_to_ws(self):
        """
        Read LSP messages from clangd stdout, strip framing, send JSON text via WS.
        """
        reader = self.proc.stdout
        while True:
            body = await lsp_read_message(reader)  # bytes
            # clangd always sends UTF-8 JSON
            await self.send(text_data=body.decode("utf-8"))

    async def _log_stderr(self):
        while True:
            line = await self.proc.stderr.readline()
            if not line:
                break
            # you may want to throttle/redirect this to your logging
            print("[clangd]", line.decode(errors="ignore").rstrip())

