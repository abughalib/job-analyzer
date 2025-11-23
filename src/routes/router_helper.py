import logging
from pathlib import Path

import xxhash
from fastapi import WebSocket, UploadFile
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from routes.models import APISTATUS

logger = logging.getLogger(__name__)
from utils.vars import get_app_path
from llm.inference import Inference
from llm.tools.layoff_tools import (
    get_recent_layoff_tool,
    get_recent_layoff_tool_fields,
)
from llm.tools.news_tools import (
    search_recent_news_tool,
)
from llm.tools.langsearch_tools import (
    search_recent_web_content_tool,
)
from llm.tools.google_search_tools import (
    google_search_tool,
)
from llm.tools.glassdoor_tools import (
    search_job_salary_tool,
)
from llm.tools.analysis_tools import (
    analyze_job_description_tool,
    analyze_resume_tool,
    analyze_candidate_fit_tool,
)
from llm.tools.document_tools import get_uploaded_document_tool
from job_analyzer.database.models import LayOff
from job_analyzer.database.layoff_db import add_layoff_bulk
from llm.tools.tool_helper import functional_call_handler as tool_handler
from utils.constants import UPLOADED_FILE_FOLDER
from utils.llm_config import get_system_prompt


class ConnectionManager:
    """WebSocket Connection Manager"""

    def __init__(self):
        logger.debug("Initializing WebSocket Connection Manager")
        self.active_connections: list[WebSocket] = []
        self.chat_history: dict[WebSocket, list[BaseMessage]] = {}
        self.document_context: dict[WebSocket, dict[str, str]] = (
            {}
        )  # Stores uploaded document IDs

    async def connect(self, websocket: WebSocket):
        """Handle websocket connection"""
        client_id = id(websocket)
        logger.info(f"Accepting new WebSocket connection from client {client_id}")

        await websocket.accept()
        self.active_connections.append(websocket)
        self.chat_history[websocket] = [
            SystemMessage(content="You are a helpful assistant.")
        ]

        logger.debug(
            f"Client {client_id} connected. Active connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        """Handle websocket disconnect"""
        client_id = id(websocket)
        logger.info(f"Disconnecting client {client_id}")

        try:
            self.active_connections.remove(websocket)
            del self.chat_history[websocket]
            if websocket in self.document_context:
                del self.document_context[websocket]
            logger.debug(
                f"Client {client_id} disconnected. Remaining connections: {len(self.active_connections)}"
            )
        except (ValueError, KeyError) as e:
            logger.error(f"Error disconnecting client {client_id}: {str(e)}")

    async def broadcast(self, message: str):
        """Broadcast websocket message"""
        logger.debug(
            f"Broadcasting message to {len(self.active_connections)} clients: {message[:100]}..."
        )

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                client_id = id(connection)
                logger.error(f"Failed to broadcast to client {client_id}: {str(e)}")

    async def handle_chat_completion(self, websocket: WebSocket, message: str):
        """Handle chat completion logic"""
        client_id = id(websocket)
        logger.debug(f"Processing chat completion for client {client_id}")
        logger.debug(f"Received message: {message[:100]}...")  # Log first 100 chars

        self.chat_history[websocket][0] = SystemMessage(content=get_system_prompt())
        self.chat_history[websocket].append(HumanMessage(content=message))
        logger.debug(
            f"Updated chat history for client {client_id}. History length: {len(self.chat_history[websocket])}"
        )

        try:
            logger.debug(f"Setting up inference engine for client {client_id}")
            inference = (
                Inference()
                .with_tools(
                    [
                        get_recent_layoff_tool,
                        get_recent_layoff_tool_fields,
                        search_recent_news_tool,
                        search_recent_web_content_tool,
                        google_search_tool,
                        search_job_salary_tool,
                        analyze_job_description_tool,
                        analyze_resume_tool,
                        analyze_candidate_fit_tool,
                        get_uploaded_document_tool,
                    ]
                )
                .with_tool_handler(tool_handler)
            )

            logger.debug(f"Starting inference stream for client {client_id}")
            await inference.stream(websocket, self.chat_history[websocket])
            logger.debug(f"Completed inference stream for client {client_id}")

        except Exception as e:
            logger.error(
                f"Error during chat completion for client {client_id}: {str(e)}",
                exc_info=True,
            )
            raise


async def handle_layoff_file_upload(file: UploadFile) -> APISTATUS:
    """Handle the upload and processing of layoff data CSV files."""
    logger.info(f"Starting layoff file upload process for: {file.filename}")

    try:
        contents = await file.read()
        file_hash = xxhash.xxh64(contents).hexdigest()
        file_extension = Path(file.filename or "abc.csv").suffix

        upload_path = (
            get_app_path()
            .joinpath(UPLOADED_FILE_FOLDER)
            .joinpath(f"temp_{file_hash}.{file_extension}")
        )
        logger.debug(f"Generated upload path: {upload_path}")

        if upload_path.exists():
            logger.warning(f"Duplicate file detected with hash {file_hash}")
            return APISTATUS.DUPLICATE

        try:
            logger.debug(f"Writing file contents to {upload_path}")
            with open(upload_path, "wb") as f:
                f.write(contents)
        except PermissionError as e:
            logger.error(f"Permission denied while writing to {upload_path}: {str(e)}")
            return APISTATUS.PERMISSIONERROR
        except Exception as e:
            logger.error(
                f"Unexpected error while writing file: {str(e)}", exc_info=True
            )
            raise

        logger.debug(f"Parsing CSV file: {upload_path}")
        layoff_parsed = LayOff.from_csv(upload_path)
        logger.info(
            f"Successfully parsed {len(layoff_parsed)} layoff records from {file.filename}"
        )

        logger.debug("Adding parsed records to database")
        await add_layoff_bulk(layoff_parsed)
        logger.info(f"Successfully added {len(layoff_parsed)} records to database")

        return APISTATUS.OK

    except Exception as e:
        logger.error(
            f"Error processing layoff file {file.filename}: {str(e)}", exc_info=True
        )
        raise
