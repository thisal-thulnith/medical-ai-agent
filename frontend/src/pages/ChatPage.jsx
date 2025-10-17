import { useState, useEffect, useRef } from 'react';
import { chatAPI, uploadAPI } from '../lib/api';
import { useChatStore, useAuthStore } from '../lib/store';
import { Send, Loader2, Paperclip, X } from 'lucide-react';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const { messages, addMessage, currentConversation, setCurrentConversation } = useChatStore();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload only PDF, JPG, or PNG files');
      return;
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    setUploadedFile(file);
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && !uploadedFile) || loading) return;

    let messageContent = input.trim();

    // If file is uploaded, upload it first
    if (uploadedFile) {
      setUploading(true);
      try {
        const formData = new FormData();
        formData.append('file', uploadedFile);
        formData.append('report_type', 'blood_test'); // Default type

        const uploadResponse = await uploadAPI.uploadReport(formData);

        // Add file info to message
        messageContent = `${messageContent}\n\n[Uploaded Medical Report: ${uploadedFile.name}]\nReport ID: ${uploadResponse.id}`;

        // Clear file
        handleRemoveFile();
      } catch (error) {
        console.error('Error uploading file:', error);
        addMessage({
          role: 'assistant',
          content: 'Sorry, failed to upload the file. Please try again.',
          timestamp: new Date().toISOString(),
        });
        setUploading(false);
        return;
      } finally {
        setUploading(false);
      }
    }

    const userMessage = {
      role: 'user',
      content: messageContent || 'Uploaded a medical report',
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage({
        message: userMessage.content,
        conversation_id: currentConversation || undefined,
        include_history: true,
      });

      if (!currentConversation) {
        setCurrentConversation(response.conversation_id);
      }

      addMessage(response.message);
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="max-w-2xl">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Welcome, {user?.full_name}! 👋
              </h2>
              <p className="text-gray-600 mb-8">
                I'm your AI medical assistant. I can help you with:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="font-semibold text-blue-900 mb-1">Symptom Analysis</div>
                  <div className="text-sm text-blue-700">Track and analyze your symptoms</div>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="font-semibold text-green-900 mb-1">Health Tracking</div>
                  <div className="text-sm text-green-700">Log vitals and medications</div>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <div className="font-semibold text-purple-900 mb-1">Medical Advice</div>
                  <div className="text-sm text-purple-700">Get health recommendations</div>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <div className="font-semibold text-orange-900 mb-1">Report Analysis</div>
                  <div className="text-sm text-orange-700">Upload and understand reports</div>
                </div>
              </div>
              <p className="text-sm text-gray-500 mt-6">
                Start by describing your health concern or question
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === 'user' ? 'bg-blue-600' : 'bg-green-600'
                  }`}
                >
                  <span className="text-white text-sm">
                    {message.role === 'user' ? '👤' : '🤖'}
                  </span>
                </div>
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">AI is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="max-w-4xl mx-auto">
          {/* File Upload Preview */}
          {uploadedFile && (
            <div className="mb-2 flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg p-2">
              <Paperclip className="w-4 h-4 text-blue-600" />
              <span className="text-sm text-blue-900 flex-1">{uploadedFile.name}</span>
              <button
                onClick={handleRemoveFile}
                className="text-blue-600 hover:text-blue-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="flex gap-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".pdf,.jpg,.jpeg,.png"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading || uploading}
              className="bg-gray-100 text-gray-700 rounded-lg px-4 py-3 hover:bg-gray-200 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              title="Upload medical report (PDF, JPG, PNG)"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your symptoms or ask a medical question..."
              className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              disabled={loading || uploading}
            />
            <button
              onClick={handleSend}
              disabled={(!input.trim() && !uploadedFile) || loading || uploading}
              className="bg-blue-600 text-white rounded-lg px-6 py-3 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {loading || uploading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line • Click 📎 to upload medical reports
          </p>
        </div>
      </div>
    </div>
  );
}
