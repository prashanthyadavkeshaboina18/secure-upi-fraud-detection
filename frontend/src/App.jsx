import { Routes, Route, Navigate } from 'react-router-dom'

import Layout from './components/layout/Layout.jsx'
import ProtectedRoute from './components/routing/ProtectedRoute.jsx'
import RoleRoute from './components/routing/RoleRoute.jsx'

import Login from './pages/auth/Login.jsx'
import Register from './pages/auth/Register.jsx'

import UserDashboard from './pages/user/UserDashboard.jsx'
import MakeTransaction from './pages/user/MakeTransaction.jsx'
import TransactionResult from './pages/user/TransactionResult.jsx'
import TransactionHistory from './pages/user/TransactionHistory.jsx'
import TransactionDetail from './pages/user/TransactionDetail.jsx'
import MyAlerts from './pages/user/MyAlerts.jsx'

import AdminDashboard from './pages/admin/AdminDashboard.jsx'
import AdminTransactions from './pages/admin/AdminTransactions.jsx'
import AdminAlerts from './pages/admin/AdminAlerts.jsx'
import AdminUsers from './pages/admin/AdminUsers.jsx'
import ModelPerformance from './pages/admin/ModelPerformance.jsx'

import NotFound from './pages/NotFound.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<UserDashboard />} />
          <Route path="/pay" element={<MakeTransaction />} />
          <Route path="/pay/result/:transactionId" element={<TransactionResult />} />
          <Route path="/transactions" element={<TransactionHistory />} />
          <Route path="/transactions/:transactionId" element={<TransactionDetail />} />
          <Route path="/alerts" element={<MyAlerts />} />

          <Route element={<RoleRoute role="ADMIN" />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/transactions" element={<AdminTransactions />} />
            <Route path="/admin/alerts" element={<AdminAlerts />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/model" element={<ModelPerformance />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
