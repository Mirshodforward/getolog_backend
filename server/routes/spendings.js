import express from 'express';
import { query } from '../config/database.js';

const router = express.Router();

// Get all spendings with pagination
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;
    const role = req.query.role; // "client" or "user" filter

    // Build WHERE clause
    let whereClause = '';
    const params = [limit, offset];

    if (role) {
      whereClause = 'WHERE role = $3';
      params.push(role);
    }

    // Get total count
    const countQuery = role
      ? 'SELECT COUNT(*) FROM spendings WHERE role = $1'
      : 'SELECT COUNT(*) FROM spendings';
    const countParams = role ? [role] : [];
    const countResult = await query(countQuery, countParams);
    const totalCount = parseInt(countResult.rows[0].count);

    // Get spendings
    const spendingsResult = await query(
      `SELECT id, role, user_id, username, amount, spend, admin_id, bot_name, created_at
       FROM spendings
       ${whereClause}
       ORDER BY created_at DESC
       LIMIT $1 OFFSET $2`,
      params
    );

    res.json({
      success: true,
      data: {
        spendings: spendingsResult.rows.map((s) => ({
          ...s,
          amount: parseFloat(s.amount) || 0,
        })),
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching spendings:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch spendings',
      message: error.message,
    });
  }
});

// Get spending statistics
router.get('/stats', async (req, res) => {
  try {
    // Client total spending
    const clientTotalResult = await query(
      "SELECT COALESCE(SUM(amount), 0) as total FROM spendings WHERE role = 'client'"
    );
    const clientTotal = parseFloat(clientTotalResult.rows[0].total) || 0;

    // User total spending
    const userTotalResult = await query(
      "SELECT COALESCE(SUM(amount), 0) as total FROM spendings WHERE role = 'user'"
    );
    const userTotal = parseFloat(userTotalResult.rows[0].total) || 0;

    // Total records
    const countResult = await query('SELECT COUNT(*) FROM spendings');
    const totalRecords = parseInt(countResult.rows[0].count);

    // Client count
    const clientCountResult = await query(
      "SELECT COUNT(*) FROM spendings WHERE role = 'client'"
    );
    const clientCount = parseInt(clientCountResult.rows[0].count);

    // User count
    const userCountResult = await query(
      "SELECT COUNT(*) FROM spendings WHERE role = 'user'"
    );
    const userCount = parseInt(userCountResult.rows[0].count);

    // Spending by type
    const byTypeResult = await query(
      `SELECT spend, COUNT(*) as count, SUM(amount) as total
       FROM spendings
       GROUP BY spend
       ORDER BY total DESC`
    );

    res.json({
      success: true,
      data: {
        client_total: clientTotal,
        user_total: userTotal,
        grand_total: clientTotal + userTotal,
        total_records: totalRecords,
        client_count: clientCount,
        user_count: userCount,
        by_type: byTypeResult.rows.map((row) => ({
          spend: row.spend,
          count: parseInt(row.count),
          total: parseFloat(row.total) || 0,
        })),
      },
    });
  } catch (error) {
    console.error('Error fetching spending stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch spending stats',
      message: error.message,
    });
  }
});

// Get spendings by user_id
router.get('/user/:userId', async (req, res) => {
  try {
    const userId = req.params.userId;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query(
      'SELECT COUNT(*) FROM spendings WHERE user_id = $1',
      [userId]
    );
    const totalCount = parseInt(countResult.rows[0].count);

    // Get spendings
    const spendingsResult = await query(
      `SELECT id, role, user_id, username, amount, spend, admin_id, bot_name, created_at
       FROM spendings
       WHERE user_id = $1
       ORDER BY created_at DESC
       LIMIT $2 OFFSET $3`,
      [userId, limit, offset]
    );

    // Get total spending
    const totalResult = await query(
      'SELECT COALESCE(SUM(amount), 0) as total FROM spendings WHERE user_id = $1',
      [userId]
    );

    res.json({
      success: true,
      data: {
        spendings: spendingsResult.rows.map((s) => ({
          ...s,
          amount: parseFloat(s.amount) || 0,
        })),
        total_spending: parseFloat(totalResult.rows[0].total) || 0,
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching user spendings:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch user spendings',
      message: error.message,
    });
  }
});

// Get spendings by admin_id (bot owner's earnings from users)
router.get('/admin/:adminId', async (req, res) => {
  try {
    const adminId = req.params.adminId;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query(
      "SELECT COUNT(*) FROM spendings WHERE admin_id = $1 AND role = 'user'",
      [adminId]
    );
    const totalCount = parseInt(countResult.rows[0].count);

    // Get spendings
    const spendingsResult = await query(
      `SELECT id, role, user_id, username, amount, spend, admin_id, bot_name, created_at
       FROM spendings
       WHERE admin_id = $1 AND role = 'user'
       ORDER BY created_at DESC
       LIMIT $2 OFFSET $3`,
      [adminId, limit, offset]
    );

    // Get total earnings
    const totalResult = await query(
      "SELECT COALESCE(SUM(amount), 0) as total FROM spendings WHERE admin_id = $1 AND role = 'user'",
      [adminId]
    );

    res.json({
      success: true,
      data: {
        spendings: spendingsResult.rows.map((s) => ({
          ...s,
          amount: parseFloat(s.amount) || 0,
        })),
        total_earnings: parseFloat(totalResult.rows[0].total) || 0,
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching admin spendings:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch admin spendings',
      message: error.message,
    });
  }
});

export default router;
