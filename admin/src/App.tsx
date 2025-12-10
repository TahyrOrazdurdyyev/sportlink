import { Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import CategoriesPage from './pages/CategoriesPage'
import CourtsPage from './pages/CourtsPage'
import TariffsPage from './pages/TariffsPage'
import TournamentsPage from './pages/TournamentsPage'
import UsersPage from './pages/UsersPage'
import ReportsPage from './pages/ReportsPage'
import { useAuthStore } from './stores/authStore'

const theme = createTheme({
  palette: {
    primary: {
      main: '#FF7A00',
    },
    secondary: {
      main: '#6B6B6B',
    },
    background: {
      default: '#F5F5F5',
    },
  },
})

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
          }
        />
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Layout />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="categories" element={<CategoriesPage />} />
          <Route path="courts" element={<CourtsPage />} />
          <Route path="tariffs" element={<TariffsPage />} />
          <Route path="tournaments" element={<TournamentsPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="reports" element={<ReportsPage />} />
        </Route>
      </Routes>
    </ThemeProvider>
  )
}

export default App

