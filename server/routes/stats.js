import express from 'express';
import { query } from '../config/database.js';

const router = express.Router();

// Get global statistics
router.get('/global', async (req, res) => {
  try {
    // Get total clients
    const totalClientsResult = await query('SELECT COUNT(*) as count FROM clients');
    const totalClients = parseInt(totalClientsResult.rows[0].count) || 0;

    // Get premium clients
    const premiumClientsResult = await query(
      "SELECT COUNT(*) as count FROM clients WHERE plan_type = 'premium'"
    );
    const premiumClients = parseInt(premiumClientsResult.rows[0].count) || 0;

    // Get total bots
    const totalBotsResult = await query('SELECT COUNT(*) as count FROM client_bots');
    const totalBots = parseInt(totalBotsResult.rows[0].count) || 0;

    // Get active bots
    const activeBotsResult = await query(
      "SELECT COUNT(*) as count FROM client_bots WHERE status = 'active'"
    );
    const activeBots = parseInt(activeBotsResult.rows[0].count) || 0;

    // Get total users
    const totalUsersResult = await query('SELECT COUNT(*) as count FROM users');
    const totalUsers = parseInt(totalUsersResult.rows[0].count) || 0;

    // Get active users
    const activeUsersResult = await query(
      "SELECT COUNT(*) as count FROM users WHERE status = 'active'"
    );
    const activeUsers = parseInt(activeUsersResult.rows[0].count) || 0;

    // Get removed users
    const removedUsersResult = await query(
      "SELECT COUNT(*) as count FROM users WHERE status = 'removed'"
    );
    const removedUsers = parseInt(removedUsersResult.rows[0].count) || 0;

    // Get total revenue
    const totalRevenueResult = await query(
      "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE role = 'plan_purchase' AND status = 'approved'"
    );
    const totalRevenue = parseFloat(totalRevenueResult.rows[0].total) || 0;

    // Get total top-ups
    const totalTopupResult = await query(
      "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE role = 'users_topup' AND status = 'approved'"
    );
    const totalTopup = parseFloat(totalTopupResult.rows[0].total) || 0;

    // Get pending transactions
    const pendingTransResult = await query(
      "SELECT COUNT(*) as count FROM transactions WHERE status = 'pending'"
    );
    const pendingTransactions = parseInt(pendingTransResult.rows[0].count) || 0;

    // Get total transactions
    const totalTransResult = await query('SELECT COUNT(*) as count FROM transactions');
    const totalTransactions = parseInt(totalTransResult.rows[0].count) || 0;

    res.json({
      success: true,
      data: {
        clients: {
          total: totalClients,
          premium: premiumClients,
          free: totalClients - premiumClients,
        },
        bots: {
          total: totalBots,
          active: activeBots,
          inactive: totalBots - activeBots,
        },
        users: {
          total: totalUsers,
          active: activeUsers,
          removed: removedUsers,
        },
        revenue: {
          total: totalRevenue,
          topups: totalTopup,
          combined: totalRevenue + totalTopup,
        },
        transactions: {
          total: totalTransactions,
          pending: pendingTransactions,
          approved: totalTransactions - pendingTransactions,
        },
      },
    });
  } catch (error) {
    console.error('Error fetching global stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch statistics',
      message: error.message,
    });
  }
});

// Get detailed dashboard statistics
router.get('/dashboard', async (req, res) => {
  try {
    // Get revenue breakdown
    const revenueBreakdownResult = await query(`
      SELECT 
        role,
        COUNT(*) as count,
        COALESCE(SUM(amount), 0) as total
      FROM transactions
      WHERE status = 'approved'
      GROUP BY role
    `);

    // Get daily revenue (last 7 days)
    const dailyRevenueResult = await query(`
      SELECT 
        DATE(created_at) as date,
        COALESCE(SUM(amount), 0) as total
      FROM transactions
      WHERE status = 'approved' 
        AND created_at >= NOW() - INTERVAL '7 days'
      GROUP BY DATE(created_at)
      ORDER BY date DESC
    `);

    // Get client registration trend (last 7 days)
    const clientTrendResult = await query(`
      SELECT 
        DATE(created_at) as date,
        COUNT(*) as count
      FROM clients
      WHERE created_at >= NOW() - INTERVAL '7 days'
      GROUP BY DATE(created_at)
      ORDER BY date DESC
    `);

    // Get bot status breakdown
    const botStatusResult = await query(`
      SELECT 
        status,
        COUNT(*) as count
      FROM client_bots
      GROUP BY status
    `);

    // Get user status breakdown
    const userStatusResult = await query(`
      SELECT 
        status,
        COUNT(*) as count
      FROM users
      GROUP BY status
    `);

    // Get plan type distribution
    const planDistributionResult = await query(`
      SELECT 
        plan_type,
        COUNT(*) as count
      FROM clients
      GROUP BY plan_type
    `);

    // Calculate average revenue per client
    const avgRevenueResult = await query(`
      SELECT 
        COALESCE(AVG(client_revenue), 0) as average
      FROM (
        SELECT 
          c.id,
          COALESCE(SUM(t.amount), 0) as client_revenue
        FROM clients c
        LEFT JOIN transactions t ON c.user_id = t.user_id AND t.status = 'approved'
        GROUP BY c.id
      ) AS client_totals
    `);

    res.json({
      success: true,
      data: {
        revenueBreakdown: revenueBreakdownResult.rows,
        dailyRevenue: dailyRevenueResult.rows,
        clientTrend: clientTrendResult.rows,
        botStatus: botStatusResult.rows,
        userStatus: userStatusResult.rows,
        planDistribution: planDistributionResult.rows,
        averageRevenuePerClient: parseFloat(avgRevenueResult.rows[0].average) || 0,
      },
    });
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch dashboard statistics',
      message: error.message,
    });
  }
});

// Get recent activity
router.get('/activity', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;

    // Get recent clients
    const recentClientsResult = await query(
      `SELECT user_id, username, phone_number, plan_type, created_at
       FROM clients
       ORDER BY created_at DESC
       LIMIT $1`,
      [limit]
    );

    // Get recent bots
    const recentBotsResult = await query(
      `SELECT bot_name, status, created_at, user_id
       FROM client_bots
       ORDER BY created_at DESC
       LIMIT $1`,
      [limit]
    );

    // Get recent transactions
    const recentTransactionsResult = await query(
      `SELECT id, user_id, username, amount, role, status, created_at
       FROM transactions
       ORDER BY created_at DESC
       LIMIT $1`,
      [limit]
    );

    // Get recent users
    const recentUsersResult = await query(
      `SELECT u.id, u.user_id, u.username, u.name, u.status, u.admin_id, u.created_at,
              c.username as owner_username
       FROM users u
       LEFT JOIN clients c ON u.admin_id = c.user_id
       ORDER BY u.created_at DESC
       LIMIT $1`,
      [limit]
    );

    res.json({
      success: true,
      data: {
        recentClients: recentClientsResult.rows,
        recentBots: recentBotsResult.rows,
        recentTransactions: recentTransactionsResult.rows,
        recentUsers: recentUsersResult.rows,
      },
    });
  } catch (error) {
    console.error('Error fetching activity:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch activity',
      message: error.message,
    });
  }
});

// Get comprehensive dashboard data
router.get('/comprehensive', async (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];

    // ========== CLIENTS SECTION ==========
    // Total clients
    const totalClientsResult = await query('SELECT COUNT(*) as count FROM clients');
    const totalClients = parseInt(totalClientsResult.rows[0].count) || 0;

    // Clients who created bots
    const clientsWithBotsResult = await query(`
      SELECT COUNT(DISTINCT user_id) as count FROM client_bots
    `);
    const clientsWithBots = parseInt(clientsWithBotsResult.rows[0].count) || 0;

    // Free plan clients (among bot creators)
    const freeBotsResult = await query(`
      SELECT COUNT(*) as count FROM client_bots WHERE status = 'free' OR status IS NULL
    `);
    const freeBots = parseInt(freeBotsResult.rows[0].count) || 0;

    // Premium/Active plan clients (among bot creators)
    const premiumBotsResult = await query(`
      SELECT COUNT(*) as count FROM client_bots WHERE status = 'active'
    `);
    const premiumBots = parseInt(premiumBotsResult.rows[0].count) || 0;

    // Active/Running bots - use status field instead
    const activeBotCount = await query(`
      SELECT COUNT(*) as count FROM client_bots WHERE status != 'inactive' AND status IS NOT NULL
    `);
    const runningBots = parseInt(activeBotCount.rows[0].count) || 0;

    // Today's new clients
    const todayClientsResult = await query(`
      SELECT COUNT(*) as count FROM clients 
      WHERE DATE(created_at) = $1
    `, [today]);
    const todayClients = parseInt(todayClientsResult.rows[0].count) || 0;

    // Last 5 clients
    const lastClientsResult = await query(`
      SELECT user_id, username, phone_number, plan_type, created_at
      FROM clients
      ORDER BY created_at DESC
      LIMIT 5
    `);

    // ========== USERS SECTION ==========
    // Total users
    const totalUsersResult = await query('SELECT COUNT(*) as count FROM users');
    const totalUsers = parseInt(totalUsersResult.rows[0].count) || 0;

    // Active users
    const activeUsersResult = await query(`
      SELECT COUNT(*) as count FROM users WHERE status = 'active'
    `);
    const activeUsers = parseInt(activeUsersResult.rows[0].count) || 0;

    // Today's new users
    const todayUsersResult = await query(`
      SELECT COUNT(*) as count FROM users 
      WHERE DATE(created_at) = $1
    `, [today]);
    const todayUsers = parseInt(todayUsersResult.rows[0].count) || 0;

    // Last 5 users
    const lastUsersResult = await query(`
      SELECT u.id, u.user_id, u.username, u.name, u.status, u.balance, u.admin_id, u.created_at,
             c.username as owner_username
      FROM users u
      LEFT JOIN clients c ON u.admin_id = c.user_id
      ORDER BY u.created_at DESC
      LIMIT 5
    `);

    // ========== CLIENTS TRANSACTIONS SECTION ==========
    // Today's successful client topups (plan_purchase)
    const todayClientTopupsResult = await query(`
      SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
      FROM transactions 
      WHERE role = 'plan_purchase' AND status = 'approved' AND DATE(created_at) = $1
    `, [today]);
    const todayClientTopups = {
      count: parseInt(todayClientTopupsResult.rows[0].count) || 0,
      total: parseFloat(todayClientTopupsResult.rows[0].total) || 0
    };

    // Total revenue from clients (plan_purchase)
    const totalClientRevenueResult = await query(`
      SELECT COALESCE(SUM(amount), 0) as total
      FROM transactions 
      WHERE role = 'plan_purchase' AND status = 'approved'
    `);
    const totalClientRevenue = parseFloat(totalClientRevenueResult.rows[0].total) || 0;

    // ========== USERS TRANSACTIONS SECTION ==========
    // Today's successful user topups
    const todayUserTopupsResult = await query(`
      SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
      FROM transactions 
      WHERE role = 'users_topup' AND status = 'approved' AND DATE(created_at) = $1
    `, [today]);
    const todayUserTopups = {
      count: parseInt(todayUserTopupsResult.rows[0].count) || 0,
      total: parseFloat(todayUserTopupsResult.rows[0].total) || 0
    };

    // Total revenue from users
    const totalUserRevenueResult = await query(`
      SELECT COALESCE(SUM(amount), 0) as total
      FROM transactions 
      WHERE role = 'users_topup' AND status = 'approved'
    `);
    const totalUserRevenue = parseFloat(totalUserRevenueResult.rows[0].total) || 0;

    // ========== PENDING TRANSACTIONS ==========
    const pendingTransResult = await query(`
      SELECT COUNT(*) as count FROM transactions WHERE status = 'pending'
    `);
    const pendingTransactions = parseInt(pendingTransResult.rows[0].count) || 0;

    // ========== SPENDING STATISTICS ==========
    // Client premium purchases (from spendings table)
    const clientSpendingResult = await query(`
      SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
      FROM spendings
      WHERE role = 'client'
    `);
    const clientSpending = {
      count: parseInt(clientSpendingResult.rows[0].count) || 0,
      total: parseFloat(clientSpendingResult.rows[0].total) || 0
    };

    // User subscription purchases by type
    const userSpendingByTypeResult = await query(`
      SELECT
        spend,
        COUNT(*) as count,
        COALESCE(SUM(amount), 0) as total
      FROM spendings
      WHERE role = 'user'
      GROUP BY spend
    `);

    // Parse user spending by type
    const userSpendingByType = {
      '1 oy': { count: 0, total: 0 },
      '1 yil': { count: 0, total: 0 },
      'cheksiz': { count: 0, total: 0 }
    };

    let totalUserSpendingCount = 0;
    let totalUserSpendingAmount = 0;

    userSpendingByTypeResult.rows.forEach(row => {
      const spend = row.spend;
      const count = parseInt(row.count) || 0;
      const total = parseFloat(row.total) || 0;

      if (userSpendingByType[spend] !== undefined) {
        userSpendingByType[spend] = { count, total };
      }
      totalUserSpendingCount += count;
      totalUserSpendingAmount += total;
    });

    // Today's spendings
    const todayClientSpendingResult = await query(`
      SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
      FROM spendings
      WHERE role = 'client' AND DATE(created_at) = $1
    `, [today]);
    const todayClientSpending = {
      count: parseInt(todayClientSpendingResult.rows[0].count) || 0,
      total: parseFloat(todayClientSpendingResult.rows[0].total) || 0
    };

    const todayUserSpendingResult = await query(`
      SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
      FROM spendings
      WHERE role = 'user' AND DATE(created_at) = $1
    `, [today]);
    const todayUserSpending = {
      count: parseInt(todayUserSpendingResult.rows[0].count) || 0,
      total: parseFloat(todayUserSpendingResult.rows[0].total) || 0
    };

    res.json({
      success: true,
      data: {
        clients: {
          total: totalClients,
          withBots: clientsWithBots,
          freeBots: freeBots,
          premiumBots: premiumBots,
          todayNew: todayClients,
          lastFive: lastClientsResult.rows
        },
        bots: {
          active: runningBots
        },
        users: {
          total: totalUsers,
          active: activeUsers,
          todayNew: todayUsers,
          lastFive: lastUsersResult.rows
        },
        clientTransactions: {
          todayCount: todayClientTopups.count,
          todayTotal: todayClientTopups.total,
          totalRevenue: totalClientRevenue
        },
        userTransactions: {
          todayCount: todayUserTopups.count,
          todayTotal: todayUserTopups.total,
          totalRevenue: totalUserRevenue
        },
        pending: pendingTransactions,
        // Spending statistics
        spendings: {
          clients: {
            total: clientSpending.count,
            amount: clientSpending.total,
            todayCount: todayClientSpending.count,
            todayAmount: todayClientSpending.total
          },
          users: {
            total: totalUserSpendingCount,
            amount: totalUserSpendingAmount,
            todayCount: todayUserSpending.count,
            todayAmount: todayUserSpending.total,
            byType: userSpendingByType
          }
        }
      }
    });
  } catch (error) {
    console.error('Error fetching comprehensive stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch comprehensive statistics',
      message: error.message
    });
  }
});

export default router;
