import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Chip,
} from '@mui/material'
import { Send as SendIcon, Notifications as NotificationsIcon } from '@mui/icons-material'
import { useTranslation } from 'react-i18next'
import apiClient from '../api/client'

interface NotificationStats {
  total_users: number
  users_with_tokens: number
  users_without_tokens: number
}

const NotificationsPage = () => {
  const { t } = useTranslation()
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [notificationType, setNotificationType] = useState('all')
  const [fcmToken, setFcmToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [alertMessage, setAlertMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [stats, setStats] = useState<NotificationStats | null>(null)
  const [sentCount, setSentCount] = useState<number | null>(null)
  const [failedCount, setFailedCount] = useState<number | null>(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/admin/notifications/stats/')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleSend = async () => {
    if (!title.trim() || !body.trim()) {
      setAlertMessage({ type: 'error', text: 'Title and body are required' })
      return
    }

    if (notificationType === 'test' && !fcmToken.trim()) {
      setAlertMessage({ type: 'error', text: 'FCM token is required for test notifications' })
      return
    }

    setLoading(true)
    setAlertMessage(null)
    setSentCount(null)
    setFailedCount(null)

    try {
      const payload: any = {
        title,
        body,
        type: notificationType,
      }

      if (notificationType === 'test') {
        payload.test_token = fcmToken
      }

      const response = await apiClient.post('/admin/notifications/send/', payload)

      if (response.data.success) {
        setAlertMessage({ type: 'success', text: t('notificationSent') })
        setSentCount(response.data.sent_count || 0)
        setFailedCount(response.data.failed_count || 0)
        
        // Clear form
        setTitle('')
        setBody('')
        setFcmToken('')
        
        // Refresh stats
        fetchStats()
      } else {
        setAlertMessage({ type: 'error', text: response.data.message || t('notificationFailed') })
      }
    } catch (error: any) {
      console.error('Error sending notification:', error)
      setAlertMessage({
        type: 'error',
        text: error.response?.data?.error || t('notificationFailed'),
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <NotificationsIcon sx={{ fontSize: 32, mr: 1 }} />
        <Typography variant="h4">{t('pushNotifications')}</Typography>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {t('totalUsers')}
                </Typography>
                <Typography variant="h4">{stats.total_users}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {t('usersWithTokens')}
                </Typography>
                <Typography variant="h4" color="success.main">
                  {stats.users_with_tokens}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {t('usersWithoutTokens')}
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {stats.users_without_tokens}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Alert Messages */}
      {alertMessage && (
        <Alert severity={alertMessage.type} sx={{ mb: 2 }} onClose={() => setAlertMessage(null)}>
          {alertMessage.text}
          {sentCount !== null && (
            <Box mt={1}>
              <Chip
                label={`${t('sentTo')} ${sentCount}`}
                color="success"
                size="small"
                sx={{ mr: 1 }}
              />
              {failedCount !== null && failedCount > 0 && (
                <Chip
                  label={`${t('failedTo')} ${failedCount}`}
                  color="error"
                  size="small"
                />
              )}
            </Box>
          )}
        </Alert>
      )}

      {/* Send Notification Form */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>
          {t('sendNotification')}
        </Typography>

        <Box display="flex" flexDirection="column" gap={2}>
          {/* Notification Type */}
          <FormControl fullWidth>
            <InputLabel>{t('notificationType')}</InputLabel>
            <Select
              value={notificationType}
              label={t('notificationType')}
              onChange={(e) => setNotificationType(e.target.value)}
            >
              <MenuItem value="all">{t('sendToAll')}</MenuItem>
              <MenuItem value="test">{t('testNotification')}</MenuItem>
            </Select>
          </FormControl>

          {/* FCM Token (for test) */}
          {notificationType === 'test' && (
            <TextField
              label={t('fcmToken')}
              value={fcmToken}
              onChange={(e) => setFcmToken(e.target.value)}
              fullWidth
              placeholder="e.g., dJxT9..."
              helperText="Get FCM token from mobile app logs"
            />
          )}

          {/* Title */}
          <TextField
            label={t('notificationTitle')}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
            required
          />

          {/* Body */}
          <TextField
            label={t('notificationBody')}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            fullWidth
            required
            multiline
            rows={4}
          />

          {/* Send Button */}
          <Button
            variant="contained"
            color="primary"
            onClick={handleSend}
            disabled={loading || !title.trim() || !body.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
            size="large"
          >
            {loading ? t('loading') : t('sendButton')}
          </Button>
        </Box>
      </Paper>
    </Box>
  )
}

export default NotificationsPage

