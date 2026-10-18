import os
import ast
import logging
import traceback

logger = logging.getLogger("TgMusicBot")

class BotDoctor:
    def __init__(self, client, logger_id: int):
        self.client = client
        self.logger_id = logger_id

    def inspect_and_repair_syntax(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            ast.parse(code_content)
            return True
        except SyntaxError as se:
            logger.error(f"Syntax anomaly detected in {file_path}: {se}")
            return False
        except Exception as e:
            logger.error(f"Inspection error on {file_path}: {e}")
            return False

    async def report_critical_issue(self, filename: str, error_details: str):
        if not self.logger_id:
            return
        alert_msg = (
            f"🚨 **[ AUTO-DIAGNOSTIC CRITICAL ALERT ]** 🚨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📁 **Affected Module:** `{filename}`\n"
            f"⚠️ **Error Diagnosis:**\n```python\n{error_details[:1000]}\n```"
        )
        try:
            await self.client.send_message(self.logger_id, alert_msg)
        except Exception as ex:
            logger.error(f"Failed to dispatch doctor alert: {ex}")

    async def handle_runtime_exception(self, module_name: str, exception: Exception):
        tb_str = traceback.format_exc()
        logger.error(f"Runtime anomaly in {module_name}: {exception}")
        await self.report_critical_issue(module_name, f"{str(exception)}\n\nTraceback:\n{tb_str}")