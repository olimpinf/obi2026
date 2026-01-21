# websockets/lsp_consumer.py
import logging
import asyncio
import os
import json
import glob
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('obi')

def lsp_frame(json_bytes: bytes) -> bytes:
    return b"Content-Length: " + str(len(json_bytes)).encode() + b"\r\n\r\n" + json_bytes

async def lsp_read_message(stream: asyncio.StreamReader) -> bytes:
    headers = b""
    while b"\r\n\r\n" not in headers:
        chunk = await stream.readuntil(b"\r\n")
        headers += chunk
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

    body = await stream.readexactly(content_length)
    return body

class LspConsumer(AsyncWebsocketConsumer):
    
    # Configuration for production vs development
    DEBUG_MODE = os.environ.get('LSP_DEBUG', 'false').lower() == 'true'
    LOG_PROTOCOL = os.environ.get('LSP_LOG_PROTOCOL', 'false').lower() == 'true'
    
    compile_commands_json_tpl = r'''[
    {
    "directory": "%(workspace)s",
    "command": "/usr/bin/clang++ -std=c++20 -I%(workspace)s -I/usr/include/c++/13 -I/usr/include/x86_64-linux-gnu/c++/13 -I/usr/include/c++/13/backward -I/usr/lib/gcc/x86_64-linux-gnu/13/include -I/usr/local/include -I/usr/include/x86_64-linux-gnu -I/usr/include %(workspace)s/main.cpp",
    "file": "%(workspace)s/main.cpp"
    }
]
'''

    async def connect(self):
        await self.accept()


        try:
            # 1. Get user ID
            # user_id = str(self.scope['user'].id)
            # if not self.scope['user'].is_authenticated:
            #     logger.info("LSP connection for anonymous user rejected")
            #     await self.close(code=4001)
            #     return
            user_id = '00000-A'
        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            await self.close(code=4002)
            return
        
        try:
            self.language_id = self.scope['url_route']['kwargs']['language_id']
        except KeyError:
            logger.warn("LSP connection without language_id rejected")
            await self.close(code=4003)
            return

        logger.info(f"LSP connect for user '{user_id}' language '{self.language_id}'")

        cmd_list = None
        cmd_string = None
        lsp_env = os.environ.copy()
        self.workspace = None
        
        if self.language_id == 'cpp':
            base_workspace = "/home/olimpinf/clangd_workspaces"
            self.workspace = os.path.join(base_workspace, user_id)
            os.makedirs(self.workspace, exist_ok=True)
            
            main_file = os.path.join(self.workspace, "main.cpp")
            if not os.path.exists(main_file):
                with open(main_file, 'w') as f:
                    f.write("// Digite seu código aqui\n")

            compile_commands_file = os.path.join(self.workspace, "compile_commands.json")
            with open(compile_commands_file, 'w') as f:
                f.write(self.compile_commands_json_tpl % {'workspace': self.workspace})

            self.stderr_prefix = "[clangd]"
            cmd = os.environ.get("CLANGD_CMD", "clangd")
            args = [
                "--enable-config",
                #"--background-index",
                #"--clang-tidy",
                "--header-insertion=never",
                f"--compile-commands-dir={self.workspace}",
            ]
            cmd_list = [cmd] + args

        elif self.language_id == 'python':
            base_workspace = "/home/olimpinf/python_workspaces" 
            self.workspace = os.path.join(base_workspace, user_id)
            os.makedirs(self.workspace, exist_ok=True)

            main_file = os.path.join(self.workspace, "main.py")
            if not os.path.exists(main_file):
                with open(main_file, 'w') as f:
                    f.write("# Digite seu código aqui\n")

            self.stderr_prefix = "[pylsp]"
            cmd = "pylsp"
            args = []
            cmd_list = [cmd] + args

        elif self.language_id == 'java':
            # 1. Define paths
            base_workspace = "/home/olimpinf/java_workspaces"
            self.workspace = os.path.join(base_workspace, user_id)
            os.makedirs(self.workspace, exist_ok=True)
            
            # Create .project file for Eclipse project
            project_file = os.path.join(self.workspace, ".project")
            if not os.path.exists(project_file):
                with open(project_file, 'w') as f:
                    f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>workspace_{user_id}</name>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.jdt.core.javabuilder</name>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.jdt.core.javanature</nature>
    </natures>
</projectDescription>
''')

            # Create .classpath file
            classpath_file = os.path.join(self.workspace, ".classpath")
            if not os.path.exists(classpath_file):
                with open(classpath_file, 'w') as f:
                    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <classpathentry kind="src" path=""/>
    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>
    <classpathentry kind="output" path="bin"/>
</classpath>
''')

            # Create a proper Java file (NOT main.java, use tarefa.java to match your template)
            java_file = os.path.join(self.workspace, "tarefa.java")
            if not os.path.exists(java_file):
                with open(java_file, 'w') as f:
                    f.write('''// ========================
// Compilador online da OBI
// ========================

public class tarefa {
    public static void main(String[] args) {
        // Digite seu código aqui
        
    }
}
''')

            jdtls_dist_path = "/usr/local/bin/jdtls"
            
            # 2. Set JAVA_HOME and JVM options
            lsp_env = os.environ.copy()
            java_home_path = "/usr/lib/jvm/java-21-openjdk-amd64" 
            lsp_env["JAVA_HOME"] = java_home_path
            lsp_env.pop("CLIENT_PORT", None)
            lsp_env.pop("CLIENT_HOST", None)
            
            # Memory tuning for concurrent users
            # Xmx: Max heap size (reduce for more concurrent users)
            # Xms: Initial heap size (same as Xmx for predictable memory)
            # XX:+UseG1GC: Better garbage collection for server workloads
            # XX:MaxMetaspaceSize: Limit for class metadata
            lsp_env["JAVA_OPTS"] = (
                "-Xmx256M "  # Reduce from 1G to 256MB per student
                "-Xms256M "  # Set initial = max for consistency
                "-XX:+UseG1GC "  # Better GC for server
                "-XX:MaxMetaspaceSize=128M "  # Limit metadata
                "-XX:+UseStringDeduplication "  # Save memory on duplicate strings
                "-Dlog.protocol=false "  # Disable protocol logging in production
                "-Dlog.level=WARNING"  # Only show warnings/errors
            )
            
            logger.info(f"[jdt.ls] Set JAVA_HOME to: {java_home_path}")
            
            self.stderr_prefix = "[jdt.ls]"
            
            # 3. Build the command with proper JVM arguments
            cmd_path = os.path.join(jdtls_dist_path, "bin/jdtls")
            config_path = os.path.join(jdtls_dist_path, "config_linux")
            
            # Add JVM arguments for better debugging
            cmd_string = f"'{cmd_path}' -configuration '{config_path}' -data '{self.workspace}' -Dlog.level=ALL"
            
            logger.info(f"[jdt.ls] Shell command: {cmd_string}")
            logger.info(f"[jdt.ls] Workspace: {self.workspace}")
        
        if cmd_string:
            self.proc = await asyncio.create_subprocess_shell(
                cmd_string,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace,
                env=lsp_env 
            )
        elif cmd_list:
            self.proc = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace,
                env=lsp_env
            )
        else:
            logger.error("No command was prepared.")
            return

        self.to_ws = asyncio.create_task(self._pump_to_ws())
        self.stderr_task = asyncio.create_task(self._log_stderr())
        logger.info(f"[{self.language_id}] LSP server started successfully")
        
    async def disconnect(self, code):
        logger.info(f"LSP disconnect code={code}")
        try:
            if self.to_ws: self.to_ws.cancel()
            if self.stderr_task: self.stderr_task.cancel()
            if self.proc and self.proc.returncode is None:
                self.proc.kill()
        except Exception:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        if not self.proc or not self.proc.stdin:
            return
        data = None
        if text_data is not None:
            data = text_data.encode("utf-8")
        elif bytes_data is not None:
            data = bytes_data
        if data is None:
            return

        # Log LSP messages for debugging (optional, can be removed later)
        try:
            msg = json.loads(data)
            logger.info(f"[{self.language_id}] Client->Server: {msg.get('method', 'response')} id={msg.get('id', 'N/A')}")
        except:
            pass

        try:
            self.proc.stdin.write(lsp_frame(data))
            await self.proc.stdin.drain()
        except (BrokenPipeError, ConnectionResetError):
            await self.close(code=1011)

    async def _pump_to_ws(self):
        reader = self.proc.stdout
        while True:
            body = await lsp_read_message(reader)
            
            # Log LSP responses for debugging (optional)
            try:
                msg = json.loads(body)
                logger.info(f"[{self.language_id}] Server->Client: {msg.get('method', 'response')} id={msg.get('id', 'N/A')}")
            except:
                pass
                
            await self.send(text_data=body.decode("utf-8"))

    async def _log_stderr(self):
        while True:
            line = await self.proc.stderr.readline()
            if not line:
                break
            logger.info(f"{self.stderr_prefix} {line.decode(errors='ignore').rstrip()}")
