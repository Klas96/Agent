"""
Integration tests for email threading functionality.

This module tests the complete email threading flow from receiving
an email to sending a properly threaded reply.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules we want to test
from src.pocketflow.nodes.email.tokenless_send import TokenlessSendEmailNode
from src.pocketflow.nodes.email.send import SendEmailNode
from src.pocketflow.services.email_service import EmailService
from src.pocketflow.core.types import SharedState, EmailSendRequest
from src.pocketflow.config.settings import Settings


class TestEmailIntegration:
    """Integration tests for email threading functionality."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.EMAIL_USERNAME = "agent@klasholmgren.se"
        settings.EMAIL_PASSWORD = "test_password"
        settings.EMAIL_HOST = "mailcluster.loopia.se"
        settings.EMAIL_PORT = 587
        settings.EMAIL_USE_TLS = True
        return settings
    
    @pytest.fixture
    def shared_state(self):
        """Create mock shared state with realistic email data."""
        shared = SharedState()
        shared.email = {
            "id": "677",
            "subject": "",  # Empty subject like real emails
            "from": "taktux <nallenalle99@gmail.com>",
            "to": "agent@klasholmgren.se",
            "body": "dfasgdfahd\r\n",  # Real email content
            "message_id": "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>",
            "in_reply_to": None,
            "references": None,
            "thread_id": "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>",
            "received_at": datetime.now()
        }
        
        # Mock agent action (what the agent decides to do)
        shared.agent_action = {
            "action": "send",
            "parameters": {
                "to": "nallenalle99@gmail.com",
                "body": "Hi nallenalle99@gmail.com! I'm your email assistant, and I'm here to help you with all your emailing needs. Our service allows me to assist you with emails, content generation, and research. If you'd like to use the full service, you can purchase tokens. I'll include payment details in this response if you're interested in getting started! To get started, you can start by typing a message, and I'll help you from there. Additionally, I'll provide you with a personal Bitcoin address if you choose to purchase tokens."
            }
        }
        
        # Mock payment info (set by PurchaseTokensWithBitcoinNode)
        shared.reply_body = "To buy 10 tokens, send 0.00000085 BTC (≈ $0.10) to your personal address: bc16eee6b9a0c1c91fc474ff40fa31b1385b0.\nCurrent BTC/USD price: $118224.00 (1 token = $0.0100)\nOnce payment is received, your tokens will be credited automatically."
        return shared

    def test_complete_tokenless_email_flow(self, mock_settings, shared_state):
        """Test the complete tokenless email flow with threading."""
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the complete flow
                prep_result = node.prep(shared_state)
                assert prep_result is not None, "Prep should return valid result"
                
                exec_result = node.exec(prep_result)
                assert exec_result is True, "Exec should return True"
                
                # Verify the email was sent with correct threading
                mock_email_service.send_email.assert_called_once()
                call_args = mock_email_service.send_email.call_args[0][0]
                
                # Verify threading headers
                assert call_args.subject == "", "Subject should be empty for proper threading"
                assert call_args.in_reply_to == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To should match original message ID"
                assert call_args.references == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "References should match original message ID"
                
                # Verify email content
                assert "Hi nallenalle99@gmail.com!" in call_args.body, "Should contain agent greeting"
                assert "To buy 10 tokens" in call_args.body, "Should contain payment info"
                assert call_args.to == "nallenalle99@gmail.com", "Should send to correct recipient"

    def test_complete_regular_email_flow(self, mock_settings, shared_state):
        """Test the complete regular email flow with threading."""
        with patch('src.pocketflow.nodes.email.send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Mock get_user_by_email to return a valid user
                with patch('src.pocketflow.nodes.email.send.get_user_by_email', create=True) as mock_get_user:
                    mock_get_user.return_value = {"email": "nallenalle99@gmail.com"}
                    
                    # Create the node
                    node = SendEmailNode()
                    
                    # Run the complete flow
                    prep_result = node.prep(shared_state)
                    assert prep_result is not None, "Prep should return valid result"
                    
                    exec_result = node.exec(prep_result)
                    assert exec_result is True, "Exec should return True"
                    
                    # Verify the email was sent with correct threading
                    mock_email_service.send_email.assert_called_once()
                    call_args = mock_email_service.send_email.call_args[0][0]
                    
                    # Verify threading headers
                    assert call_args.subject == "", "Subject should be empty for proper threading"
                    assert call_args.in_reply_to == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To should match original message ID"

    def test_email_service_integration(self, mock_settings):
        """Test EmailService integration with threading headers."""
        # Create email service with mock settings
        email_service = EmailService(mock_settings)
        
        # Create email send request with threading info
        request = EmailSendRequest(
            to="nallenalle99@gmail.com",
            subject="",  # Empty subject for proper threading
            body="Test email body with threading",
            in_reply_to="<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>",
            references="<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>"
        )
        
        # Mock SMTP connection
        with patch('smtplib.SMTP') as mock_smtp_class:
            mock_smtp = Mock()
            mock_smtp_class.return_value = mock_smtp
            
            # Mock the send_message method to capture the message
            captured_message = None
            def capture_send_message(msg):
                nonlocal captured_message
                captured_message = msg
                return None
            
            mock_smtp.send_message.side_effect = capture_send_message
            
            # Send the email
            result = email_service.send_email(request)
            
            # Verify email was sent successfully
            assert result is True, "Email should be sent successfully"
            
            # Verify all threading headers are set correctly
            assert captured_message is not None, "Message should be captured"
            assert captured_message['In-Reply-To'] == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To header should be set correctly"
            assert captured_message['References'] == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "References header should be set correctly"
            assert captured_message['Subject'] == "", "Subject should be empty for proper threading"
            
            # Verify additional headers for Gmail compatibility
            assert 'X-Google-Original-Message-ID' in captured_message, "Should have Gmail-specific header"
            assert 'X-Thread-Id' in captured_message, "Should have thread ID header"
            
            # Verify Message-ID format
            message_id = captured_message['Message-ID']
            assert message_id is not None, "Message-ID should be set"
            assert message_id.startswith("<pocketflow-"), "Should start with pocketflow prefix"
            assert message_id.endswith("@klasholmgren.se>"), "Should end with correct domain"

    def test_threading_with_subject_email(self, mock_settings, shared_state):
        """Test threading with an email that has a subject."""
        # Update shared state with email that has a subject
        shared_state.email["subject"] = "Test Subject"
        
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the complete flow
                prep_result = node.prep(shared_state)
                exec_result = node.exec(prep_result)
                
                # Verify the email was sent with correct threading
                mock_email_service.send_email.assert_called_once()
                call_args = mock_email_service.send_email.call_args[0][0]
                
                # Verify threading headers for subject email
                assert call_args.subject == "Re: Test Subject", "Should have Re: prefix"
                assert call_args.in_reply_to == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To should match original message ID"

    def test_error_handling_integration(self, mock_settings, shared_state):
        """Test error handling in the complete email flow."""
        # Test with missing email data
        shared_state.email = None
        
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the flow - should handle missing email gracefully
                prep_result = node.prep(shared_state)
                assert prep_result is None, "Prep should return None for missing email data"
                
                # Exec should handle None gracefully
                exec_result = node.exec(None)
                assert exec_result is None, "Exec should return None for None prep result" 