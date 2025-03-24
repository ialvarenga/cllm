import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cllm.cli import app


@pytest.fixture
def runner():
    """Set up the Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Mock the config object."""
    with patch('cllm.cli.config') as mock_config:
        # Default behavior
        mock_config.get_api_key.return_value = None
        mock_config.get.return_value = "default"
        mock_config.set = MagicMock()
        mock_config.set_api_key = MagicMock()
        yield mock_config


@pytest.fixture
def mock_config_with_api_key():
    """Mock the config object with API key set."""
    with patch('cllm.cli.config') as mock_config:
        mock_config.get_api_key.return_value = "fake-api-key"
        mock_config.get.return_value = "default"
        mock_config.set = MagicMock()
        yield mock_config


@pytest.fixture
def mock_thread_manager():
    """Mock the thread_manager object."""
    with patch('cllm.cli.thread_manager') as mock:
        mock.load_history.return_value = []
        mock.save_history = MagicMock()
        mock.list_threads.return_value = ["thread1", "thread2"]
        mock.clear_thread = MagicMock(return_value=True)
        yield mock


@pytest.fixture
def mock_openai_client():
    """Mock the OpenAI client."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Set up the response structure
        mock_message.content = "This is a test response"
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        
        # Set up the chat.completions.create method
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        yield mock_client


@pytest.fixture
def mock_console():
    """Mock the rich console."""
    with patch('cllm.cli.console') as mock:
        mock.print = MagicMock()
        yield mock


class TestAskCommand:
    """Tests for the ask command and _ask_async function."""

    def test_ask_command_basic_invocation(self, runner, mock_config_with_api_key):
        """Test basic invocation of the ask command."""
        with patch('asyncio.run') as mock_run:
            result = runner.invoke(app, ["ask", "Hello world"])
            
            assert result.exit_code == 0
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_ask_async_no_api_key(self, mock_config):
        """Test that _ask_async exits when no API key is found."""
        from cllm.cli import _ask_async
        
        with patch('cllm.cli.console') as mock_console:
            with patch('cllm.cli.sys.exit') as mock_exit:
                await _ask_async("Hello world", "gpt-3.5-turbo", 0.7, 1000, True, None)
                
                mock_console.print.assert_any_call("[bold red]API key not configured![/bold red]")
                mock_exit.assert_called_with(1)


    def test_clear_thread_existing(self, runner, mock_console):
        """Test clearing an existing thread."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink') as mock_unlink:
                result = runner.invoke(app, ["clear-thread", "test-thread"])
                
                assert result.exit_code == 0
                mock_unlink.assert_called_once()

    def test_clear_thread_nonexistent(self, runner, mock_console):
        """Test clearing a non-existent thread."""
        with patch('pathlib.Path.exists', return_value=False):
            result = runner.invoke(app, ["clear-thread", "nonexistent"])
            
            assert result.exit_code == 0
            mock_console.print.assert_called_with("[red]Thread 'nonexistent' não encontrada.[/red]")

    def test_list_threads_with_threads(self, runner, mock_thread_manager, mock_console):
        """Test listing threads when threads exist."""
        mock_thread_manager.list_threads.return_value = ["thread1", "thread2"]
        
        result = runner.invoke(app, ["list-threads"])
        
        assert result.exit_code == 0
        assert mock_thread_manager.list_threads.called
        assert mock_console.print.call_count >= 3  # Header + 2 threads

    def test_list_threads_no_threads(self, runner, mock_thread_manager, mock_console):
        """Test listing threads when no threads exist."""
        mock_thread_manager.list_threads.return_value = []
        
        result = runner.invoke(app, ["list-threads"])
        
        assert result.exit_code == 0
        assert mock_thread_manager.list_threads.called
        mock_console.print.assert_called_with("[italic]Nenhuma thread encontrada.[/italic]")