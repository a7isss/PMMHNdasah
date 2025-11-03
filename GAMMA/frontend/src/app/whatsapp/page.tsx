'use client';

import { useState } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Paper,
  Chip,
} from '@mui/material';
import { WhatsApp, Send, ArrowBack } from '@mui/icons-material';
import { useAppSelector } from '@/lib/hooks';
import Link from 'next/link';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'system';
  timestamp: Date;
  type: 'text' | 'ai_response' | 'notification';
}

export default function WhatsAppPage() {
  const { user } = useAppSelector((state) => state.auth);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Welcome to WhatsApp PM! Send messages to get AI-powered responses and project updates.',
      sender: 'system',
      timestamp: new Date(),
      type: 'notification',
    },
    {
      id: '2',
      text: 'Try: "What is the status of my projects?" or "Create a task for foundation work"',
      sender: 'system',
      timestamp: new Date(),
      type: 'ai_response',
    },
  ]);

  const handleSendMessage = () => {
    if (!message.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: message,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    };

    setMessages(prev => [...prev, newMessage]);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: `AI Response: "${message}" - This WhatsApp integration is ready for real-time project communication. Your phone number (${user?.phone || 'not set'}) should be WhatsApp-enabled for full functionality.`,
        sender: 'system',
        timestamp: new Date(),
        type: 'ai_response',
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);

    setMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Button
          component={Link}
          href="/"
          startIcon={<ArrowBack />}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          WhatsApp Integration
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time project communication and AI-powered messaging
        </Typography>
      </Box>

      <Card sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: '#25D366' }}>
          <Box display="flex" alignItems="center">
            <Avatar sx={{ bgcolor: 'white', mr: 2 }}>
              <WhatsApp sx={{ color: '#25D366' }} />
            </Avatar>
            <Box>
              <Typography variant="h6" sx={{ color: 'white' }}>
                Hndasah PM Assistant
              </Typography>
              <Typography variant="body2" sx={{ color: 'white', opacity: 0.8 }}>
                AI-powered project communication
              </Typography>
            </Box>
            <Chip
              label="Online"
              size="small"
              sx={{
                ml: 'auto',
                bgcolor: 'white',
                color: '#25D366',
                fontWeight: 'bold'
              }}
            />
          </Box>
        </Box>

        {/* Messages */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          <List>
            {messages.map((msg) => (
              <ListItem
                key={msg.id}
                sx={{
                  justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1,
                }}
              >
                <Paper
                  sx={{
                    p: 1.5,
                    maxWidth: '70%',
                    bgcolor: msg.sender === 'user' ? '#DCF8C6' : msg.type === 'ai_response' ? '#E3F2FD' : '#F5F5F5',
                    borderRadius: 2,
                  }}
                >
                  <ListItemText
                    primary={msg.text}
                    secondary={
                      msg.type === 'ai_response' ? '🤖 AI Assistant' :
                      msg.type === 'notification' ? '📢 System' :
                      new Date(msg.timestamp).toLocaleTimeString()
                    }
                    primaryTypographyProps={{
                      variant: 'body2',
                    }}
                    secondaryTypographyProps={{
                      variant: 'caption',
                      sx: { opacity: 0.7 }
                    }}
                  />
                </Paper>
              </ListItem>
            ))}
          </List>
        </Box>

        {/* Message Input */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box display="flex" gap={1}>
            <TextField
              fullWidth
              placeholder="Type your message... (e.g., 'Project status', 'Create task', 'Cost update')"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                },
              }}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!message.trim()}
              sx={{
                borderRadius: 3,
                bgcolor: '#25D366',
                '&:hover': {
                  bgcolor: '#128C7E',
                },
              }}
            >
              <Send />
            </Button>
          </Box>

          {/* Phone Number Status */}
          <Box sx={{ mt: 1, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              📱 Phone: {user?.phone ? `${user.phone} (${user.whatsappEnabled ? 'WhatsApp enabled' : 'WhatsApp not verified'})` : 'Not set - Add phone number in profile'}
            </Typography>
          </Box>
        </Box>
      </Card>

      {/* Features Info */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            WhatsApp Integration Features
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
            <Chip label="🤖 AI Message Processing" variant="outlined" />
            <Chip label="📊 Real-time Updates" variant="outlined" />
            <Chip label="✅ Task Creation" variant="outlined" />
            <Chip label="💰 Cost Tracking" variant="outlined" />
            <Chip label="🚨 Smart Notifications" variant="outlined" />
            <Chip label="📱 Mobile Optimized" variant="outlined" />
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}
