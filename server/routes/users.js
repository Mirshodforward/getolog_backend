import express from 'express';
import { query } from '../config/database.js';

const router = express.Router();

// Get all users with pagination, search, and filters
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;
    const status = req.query.status;
    const search = req.query.search;
    const ownerUsername = req.query.owner_username;
    const sortBy = req.query.sort_by || 'created_at';
    const sortOrder = req.query.sort_order || 'DESC';

    // Allowed sort fields
    const allowedSorts = ['created_at', 'balance', 'username', 'name', 'status'];
    const safeSortBy = allowedSorts.includes(sortBy) ? sortBy : 'created_at';
    const safeSortOrder = sortOrder.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    // Build dynamic WHERE conditions
    const conditions = [];
    const countParams = [];
    let paramIndex = 1;

    if (status) {
      conditions.push(`u.status = $${paramIndex}`);
      countParams.push(status);
      paramIndex++;
    }

    if (search) {
      if (!isNaN(search)) {
        conditions.push(`u.user_id = $${paramIndex}`);
        countParams.push(parseInt(search));
      } else {
        conditions.push(`(u.username ILIKE $${paramIndex} OR u.name ILIKE $${paramIndex})`);
        countParams.push(`%${search}%`);
      }
      paramIndex++;
    }

    if (ownerUsername) {
      conditions.push(`c.username ILIKE $${paramIndex}`);
      countParams.push(`%${ownerUsername}%`);
      paramIndex++;
    }

    const whereClause = conditions.length > 0 ? ' WHERE ' + conditions.join(' AND ') : '';

    // Count query (needs JOIN if filtering by owner)
    const needsJoin = !!ownerUsername;
    let countQuery = needsJoin
      ? `SELECT COUNT(*) FROM users u LEFT JOIN clients c ON u.admin_id = c.user_id${whereClause}`
      : `SELECT COUNT(*) FROM users u${whereClause}`;

    const countResult = await query(countQuery, countParams);
    const totalCount = parseInt(countResult.rows[0].count);

    // Select query
    const selectParams = [...countParams, limit, offset];
    const selectQuery = `
      SELECT u.id, u.user_id, u.username, u.name, u.duration,
             u.balance, u.status, u.invite_link, u.admin_id, u.created_at,
             c.username as bot_owner_username
      FROM users u
      LEFT JOIN clients c ON u.admin_id = c.user_id
      ${whereClause}
      ORDER BY u.${safeSortBy} ${safeSortOrder}
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;

    const usersResult = await query(selectQuery, selectParams);

    // Stats query (with same filters applied)
    const statsQuery = `
      SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE u.status = 'active') as active,
        COUNT(*) FILTER (WHERE u.status = 'free') as free,
        COUNT(*) FILTER (WHERE u.status = 'removed') as removed,
        COALESCE(SUM(u.balance), 0) as total_balance
      FROM users u
      ${needsJoin ? 'LEFT JOIN clients c ON u.admin_id = c.user_id' : ''}
      ${whereClause}
    `;
    const statsResult = await query(statsQuery, countParams);
    const stats = statsResult.rows[0];

    res.json({
      success: true,
      data: {
        users: usersResult.rows.map((user) => ({
          ...user,
          balance: parseFloat(user.balance) || 0,
        })),
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
        stats: {
          total: parseInt(stats.total),
          active: parseInt(stats.active),
          free: parseInt(stats.free),
          removed: parseInt(stats.removed),
          total_balance: parseFloat(stats.total_balance) || 0,
        },
      },
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch users',
      message: error.message,
    });
  }
});

// Get user details by ID
router.get('/:userId', async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);

    // Get user info
    const userResult = await query(
      `SELECT u.*, c.username as bot_owner_username, c.user_id as bot_owner_id
       FROM users u
       LEFT JOIN clients c ON u.admin_id = c.user_id
       WHERE u.user_id = $1`,
      [userId]
    );

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'User not found',
      });
    }

    const user = userResult.rows[0];

    // Get user's transactions
    const transactionsResult = await query(
      `SELECT id, amount, role, status, created_at
       FROM transactions
       WHERE user_id = $1
       ORDER BY created_at DESC
       LIMIT 10`,
      [userId]
    );

    res.json({
      success: true,
      data: {
        user: {
          ...user,
          balance: parseFloat(user.balance) || 0,
        },
        recent_transactions: transactionsResult.rows.map((trans) => ({
          ...trans,
          amount: parseFloat(trans.amount) || 0,
        })),
      },
    });
  } catch (error) {
    console.error('Error fetching user details:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch user details',
      message: error.message,
    });
  }
});

// Search users
router.get('/search/:query', async (req, res) => {
  try {
    const searchQuery = req.params.query;

    let usersResult;

    // Check if search is numeric (user_id)
    if (!isNaN(searchQuery)) {
      usersResult = await query(
        `SELECT u.*, c.username as bot_owner_username
         FROM users u
         LEFT JOIN clients c ON u.admin_id = c.user_id
         WHERE u.user_id = $1`,
        [parseInt(searchQuery)]
      );
    } else {
      // Search by username or name
      const searchPattern = `%${searchQuery}%`;
      usersResult = await query(
        `SELECT u.*, c.username as bot_owner_username
         FROM users u
         LEFT JOIN clients c ON u.admin_id = c.user_id
         WHERE u.username ILIKE $1 OR u.name ILIKE $1
         LIMIT 20`,
        [searchPattern]
      );
    }

    res.json({
      success: true,
      data: {
        users: usersResult.rows.map((user) => ({
          ...user,
          balance: parseFloat(user.balance) || 0,
        })),
      },
    });
  } catch (error) {
    console.error('Error searching users:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to search users',
      message: error.message,
    });
  }
});

// Update user status
router.patch('/:userId/status', async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);
    const { status } = req.body;

    if (!status || !['active', 'removed', 'free'].includes(status)) {
      return res.status(400).json({
        success: false,
        error: 'Valid status is required (active, removed, or free)',
      });
    }

    const result = await query(
      'UPDATE users SET status = $1 WHERE user_id = $2 RETURNING *',
      [status, userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'User not found',
      });
    }

    res.json({
      success: true,
      data: {
        user: {
          ...result.rows[0],
          balance: parseFloat(result.rows[0].balance) || 0,
        },
      },
    });
  } catch (error) {
    console.error('Error updating user status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update user status',
      message: error.message,
    });
  }
});

// Get users by bot owner (admin_id)
router.get('/by-owner/:ownerId', async (req, res) => {
  try {
    const ownerId = parseInt(req.params.ownerId);
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query(
      'SELECT COUNT(*) FROM users WHERE admin_id = $1',
      [ownerId]
    );
    const totalCount = parseInt(countResult.rows[0].count);

    // Get users
    const usersResult = await query(
      `SELECT id, user_id, username, name, duration, balance, status,
              invite_link, created_at
       FROM users
       WHERE admin_id = $1
       ORDER BY created_at DESC
       LIMIT $2 OFFSET $3`,
      [ownerId, limit, offset]
    );

    res.json({
      success: true,
      data: {
        users: usersResult.rows.map((user) => ({
          ...user,
          balance: parseFloat(user.balance) || 0,
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
    console.error('Error fetching users by owner:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch users',
      message: error.message,
    });
  }
});

export default router;
