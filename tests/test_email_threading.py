"""
Tests for email threading functionality.

This module tests the email threading implementation to ensure
emails appear as threaded conversations in Gmail.
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


class TestEmailThreading:
    """Test cases for email threading functionality."""
    
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
        """Create mock shared state."""
        shared = SharedState()
        shared.email = {
            "id": "123",
            "subject": "",
            "from": "taktux <nallenalle99@gmail.com>",
            "to": "agent@klasholmgren.se",
            "body": "test message",
            "message_id": "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>",
            "in_reply_to": None,
            "references": None,
            "thread_id": "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>",
            "received_at": datetime.now()
        }
        
        shared.agent_action = {
            "action": "send",
            "parameters": {
                "to": "nallenalle99@gmail.com",
                "body": "Hi! I'm your email assistant. Here's how to get started..."
            }
        }
        
        shared.reply_body = "To buy 10 tokens, send 0.00000085 BTC to your personal address: bc16eee6b9a0c1c91fc474ff40fa31b1385b0."
        return shared

    def test_tokenless_send_email_node_empty_subject_threading(self, mock_settings, shared_state):
        """Test that TokenlessSendEmailNode uses empty subject for proper threading."""
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the node
                prep_result = node.prep(shared_state)
                assert prep_result is not None, "Prep should return valid result"
                
                exec_result = node.exec(prep_result)
                assert exec_result is True, "Exec should return True"
                
                # Verify that send_email was called with correct threading parameters
                mock_email_service.send_email.assert_called_once()
                call_args = mock_email_service.send_email.call_args[0][0]
                
                # Check that subject is empty for proper threading
                assert call_args.subject == "", "Subject should be empty for proper threading"
                
                # Check that In-Reply-To is set correctly
                assert call_args.in_reply_to == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To should match original message ID"
                
                # Check that References is set correctly
                assert call_args.references == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "References should match original message ID for first reply"

    def test_tokenless_send_email_node_with_subject_threading(self, mock_settings, shared_state):
        """Test that TokenlessSendEmailNode handles subjects with 'Re:' prefix correctly."""
        # Update shared state with an email that has a subject
        shared_state.email["subject"] = "Test Subject"
        
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the node
                prep_result = node.prep(shared_state)
                assert prep_result is not None, "Prep should return valid result"
                
                exec_result = node.exec(prep_result)
                assert exec_result is True, "Exec should return True"
                
                # Verify that send_email was called with correct threading parameters
                mock_email_service.send_email.assert_called_once()
                call_args = mock_email_service.send_email.call_args[0][0]
                
                # Check that subject has "Re:" prefix
                assert call_args.subject == "Re: Test Subject", "Subject should have 'Re:' prefix"
                
                # Check that In-Reply-To is set correctly
                assert call_args.in_reply_to == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To should match original message ID"

    @pytest.mark.parametrize("test_subject", [
        "Re: Test Subject",
        "RE: Test Subject", 
        "re: Test Subject"
    ])
    def test_tokenless_send_email_node_existing_re_prefix_handling(self, mock_settings, shared_state, test_subject):
        """Test that TokenlessSendEmailNode handles existing 'Re:' prefixes correctly."""
        # Update shared state with test subject
        shared_state.email["subject"] = test_subject
        
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the node
                prep_result = node.prep(shared_state)
                exec_result = node.exec(prep_result)
                
                # Verify that send_email was called
                mock_email_service.send_email.assert_called_once()
                call_args = mock_email_service.send_email.call_args[0][0]
                
                # Check that subject has correct "Re:" prefix (cleaned and re-added)
                assert call_args.subject == "Re: Test Subject", f"Subject should be 'Re: Test Subject' for input '{test_subject}'"

    def test_send_email_node_empty_subject_threading(self, mock_settings, shared_state):
        """Test that SendEmailNode uses empty subject for proper threading."""
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
                    
                    # Run the node
                    prep_result = node.prep(shared_state)
                    assert prep_result is not None, "Prep should return valid result"
                    
                    exec_result = node.exec(prep_result)
                    assert exec_result is True, "Exec should return True"
                    
                    # Verify that send_email was called with correct threading parameters
                    mock_email_service.send_email.assert_called_once()
                    call_args = mock_email_service.send_email.call_args[0][0]
                    
                    # Check that subject is empty for proper threading
                    assert call_args.subject == "", "Subject should be empty for proper threading"
                    
                    # Check that In-Reply-To is set correctly
                    assert call_args.in_reply_to == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To should match original message ID"

    def test_email_service_threading_headers(self, mock_settings):
        """Test that EmailService sets threading headers correctly."""
        # Create email service with mock settings
        email_service = EmailService(mock_settings)
        
        # Create email send request with threading info
        request = EmailSendRequest(
            to="nallenalle99@gmail.com",
            subject="",
            body="Test email body",
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
            
            # Verify email was sent
            assert result is True, "Email should be sent successfully"
            
            # Verify threading headers are set correctly
            assert captured_message is not None, "Message should be captured"
            assert captured_message['In-Reply-To'] == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "In-Reply-To header should be set correctly"
            assert captured_message['References'] == "<CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>", "References header should be set correctly"
            assert captured_message['Subject'] == "", "Subject should be empty for proper threading"
            
            # Verify Message-ID is set
            assert captured_message['Message-ID'] is not None, "Message-ID should be set"
            assert captured_message['Message-ID'].startswith("<pocketflow-"), "Message-ID should start with pocketflow prefix"

    def test_email_service_message_id_format(self, mock_settings):
        """Test that EmailService generates proper Message-ID format."""
        email_service = EmailService(mock_settings)
        
        request = EmailSendRequest(
            to="nallenalle99@gmail.com",
            subject="",
            body="Test email body"
        )
        
        with patch('smtplib.SMTP') as mock_smtp_class:
            mock_smtp = Mock()
            mock_smtp_class.return_value = mock_smtp
            
            captured_message = None
            def capture_send_message(msg):
                nonlocal captured_message
                captured_message = msg
                return None
            
            mock_smtp.send_message.side_effect = capture_send_message
            
            # Send the email
            email_service.send_email(request)
            
            # Verify Message-ID format
            message_id = captured_message['Message-ID']
            assert message_id is not None, "Message-ID should be set"
            assert message_id.startswith("<pocketflow-"), "Should start with pocketflow prefix"
            assert message_id.endswith("@klasholmgren.se>"), "Should end with correct domain"
            assert "-" in message_id, "Should contain timestamp separator"

    def test_threading_with_references_chain(self, mock_settings, shared_state):
        """Test that threading works correctly with existing references chain."""
        # Update shared state with email that has existing references
        shared_state.email["references"] = "<original-message-id@example.com>"
        
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the node
                prep_result = node.prep(shared_state)
                exec_result = node.exec(prep_result)
                
                # Verify that send_email was called with correct references chain
                mock_email_service.send_email.assert_called_once()
                call_args = mock_email_service.send_email.call_args[0][0]
                
                # Check that References includes the chain
                expected_references = "<original-message-id@example.com> <CAMMd_=p+WQGp9YrOf+_tTv1oGkOZMm-stFovXVp3oPpu5B0SWQ@mail.gmail.com>"
                assert call_args.references == expected_references, "References should include the full chain"

    def test_error_handling_in_threading(self, mock_settings, shared_state):
        """Test that threading handles errors gracefully."""
        # Test with missing message_id
        shared_state.email["message_id"] = None
        
        with patch('src.pocketflow.nodes.email.tokenless_send.get_settings', return_value=mock_settings):
            with patch('src.pocketflow.nodes.email.tokenless_send.EmailService') as mock_email_service_class:
                # Mock the email service
                mock_email_service = Mock()
                mock_email_service_class.return_value = mock_email_service
                mock_email_service.send_email.return_value = True
                
                # Create the node
                node = TokenlessSendEmailNode()
                
                # Run the node - should handle missing message_id gracefully
                prep_result = node.prep(shared_state)
                assert prep_result is not None, "Prep should handle missing message_id"
                
                exec_result = node.exec(prep_result)
                assert exec_result is True, "Exec should complete successfully" 