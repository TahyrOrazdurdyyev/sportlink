import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material'
import {
  People,
  SportsBasketball,
  EmojiEvents,
  EventNote,
  TrendingUp,
  Block,
  CheckCircle,
  Schedule,
} from '@mui/icons-material'
import apiClient from '../api/client'

interface DashboardStats {
  users: {
    total: number
    active: number
    banned: number
    new_this_week: number
  }
  courts: {
    total: number
    active: number
  }
  tournaments: {
    total: number
    active: number
    upcoming: number
  }
  bookings: {
    total: number
    pending: number
    confirmed: number
    new_this_week: number
  }
}

interface User {
  id: string
  phone: string
  first_name?: string
  last_name?: string
  created_at: string
}

interface Tournament {
  id: string
  name_i18n: {
    tk?: string
    ru?: string
    en?: string
  }
  start_date: string
  status: string
}

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
  color: string
  subtitle?: string
}

const StatCard = ({ title, value, icon, color, subtitle }: StatCardProps) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4" component="div" color={color}>
            {value.toLocaleString()}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            backgroundColor: `${color}20`,
            borderRadius: 2,
            p: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
)

export default function DashboardPage() {
  const { t, i18n } = useTranslation()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentUsers, setRecentUsers] = useState<User[]>([])
  const [upcomingTournaments, setUpcomingTournaments] = useState<Tournament[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    try {
      setLoading(true)

      // Fetch statistics
      const statsResponse = await apiClient.get('/reports/dashboard/')
      setStats(statsResponse.data)

      // Fetch recent users
      const usersResponse = await apiClient.get('/admin/users/?page=1')
      const users = usersResponse.data.results || usersResponse.data
      setRecentUsers(users.slice(0, 5))

      // Fetch upcoming tournaments
      const tournamentsResponse = await apiClient.get('/admin/tournaments/')
      const tournaments = tournamentsResponse.data.results || tournamentsResponse.data
      setUpcomingTournaments(tournaments.slice(0, 5))

      setError('')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load dashboard data')
      console.error('Error loading dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const getStatusColor = (status: string) => {
    const statusMap: { [key: string]: 'success' | 'warning' | 'error' | 'info' | 'default' } = {
      registration_open: 'success',
      in_progress: 'info',
      completed: 'default',
      cancelled: 'error',
      draft: 'warning',
    }
    return statusMap[status] || 'default'
  }

  const getLocalizedName = (name_i18n: { tk?: string; ru?: string; en?: string }) => {
    const lang = i18n.language as 'tk' | 'ru' | 'en'
    return name_i18n[lang] || name_i18n.tk || name_i18n.ru || name_i18n.en || '-'
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    )
  }

  if (!stats) {
    return <Alert severity="info">No data available</Alert>
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {t('dashboard')}
      </Typography>
      <Typography variant="body1" color="textSecondary" gutterBottom sx={{ mb: 3 }}>
        {t('welcomeMessage')}
      </Typography>

      {/* Main Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('totalUsers')}
            value={stats.users.total}
            icon={<People sx={{ fontSize: 32, color: '#1976d2' }} />}
            color="#1976d2"
            subtitle={`${stats.users.new_this_week} ${t('newThisWeek')}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('activeCourts')}
            value={stats.courts.active}
            icon={<SportsBasketball sx={{ fontSize: 32, color: '#2e7d32' }} />}
            color="#2e7d32"
            subtitle={`${stats.courts.total} ${t('totalCourts')}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('tournaments')}
            value={stats.tournaments.active}
            icon={<EmojiEvents sx={{ fontSize: 32, color: '#ed6c02' }} />}
            color="#ed6c02"
            subtitle={`${stats.tournaments.upcoming} ${t('upcoming')}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('bookings')}
            value={stats.bookings.confirmed}
            icon={<EventNote sx={{ fontSize: 32, color: '#9c27b0' }} />}
            color="#9c27b0"
            subtitle={`${stats.bookings.pending} ${t('pending')}`}
          />
        </Grid>
      </Grid>

      {/* Secondary Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <TrendingUp sx={{ color: '#2e7d32' }} />
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    {t('activeUsers')}
                  </Typography>
                  <Typography variant="h6">{stats.users.active}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <Block sx={{ color: '#d32f2f' }} />
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    {t('bannedUsers')}
                  </Typography>
                  <Typography variant="h6">{stats.users.banned}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <CheckCircle sx={{ color: '#2e7d32' }} />
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    {t('confirmedBookings')}
                  </Typography>
                  <Typography variant="h6">{stats.bookings.confirmed}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <Schedule sx={{ color: '#ed6c02' }} />
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    {t('pendingBookings')}
                  </Typography>
                  <Typography variant="h6">{stats.bookings.pending}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Data Tables */}
      <Grid container spacing={3}>
        {/* Recent Users */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t('recentUsers')}
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('phone')}</TableCell>
                    <TableCell>{t('name')}</TableCell>
                    <TableCell>{t('registered')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentUsers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} align="center">
                        {t('noData')}
                      </TableCell>
                    </TableRow>
                  ) : (
                    recentUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>{user.phone}</TableCell>
                        <TableCell>
                          {user.first_name || user.last_name
                            ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                            : '-'}
                        </TableCell>
                        <TableCell>{formatDate(user.created_at)}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Upcoming Tournaments */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t('upcomingTournaments')}
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('name')}</TableCell>
                    <TableCell>{t('startDate')}</TableCell>
                    <TableCell>{t('status')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {upcomingTournaments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} align="center">
                        {t('noData')}
                      </TableCell>
                    </TableRow>
                  ) : (
                    upcomingTournaments.map((tournament) => (
                      <TableRow key={tournament.id}>
                        <TableCell>
                          {getLocalizedName(tournament.name_i18n)}
                        </TableCell>
                        <TableCell>{formatDate(tournament.start_date)}</TableCell>
                        <TableCell>
                          <Chip
                            label={tournament.status.replace('_', ' ')}
                            color={getStatusColor(tournament.status)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
