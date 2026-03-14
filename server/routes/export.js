import express from 'express';
import ExcelJS from 'exceljs';
import { query } from '../config/database.js';

const router = express.Router();

// Export all data to Excel
router.get('/all', async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();

    // ====== CLIENTS SHEET ======
    const clientsSheet = workbook.addWorksheet('Clients');
    clientsSheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'User ID', key: 'user_id', width: 15 },
      { header: 'Username', key: 'username', width: 20 },
      { header: 'Phone', key: 'phone_number', width: 15 },
      { header: 'Balance', key: 'balance', width: 15 },
      { header: 'Plan', key: 'plan_type', width: 12 },
      { header: 'Language', key: 'language', width: 10 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    // Style header
    clientsSheet.getRow(1).font = { bold: true };
    clientsSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4F81BD' },
    };
    clientsSheet.getRow(1).alignment = { horizontal: 'center' };

    const clientsResult = await query(
      'SELECT * FROM clients ORDER BY created_at DESC'
    );

    clientsResult.rows.forEach((client) => {
      clientsSheet.addRow({
        ...client,
        balance: parseFloat(client.balance) || 0,
        created_at: client.created_at
          ? new Date(client.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    // ====== BOTS SHEET ======
    const botsSheet = workbook.addWorksheet('Bots');
    botsSheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'Owner ID', key: 'user_id', width: 15 },
      { header: 'Bot Name', key: 'bot_name', width: 20 },
      { header: 'Channel ID', key: 'channel_id', width: 15 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Oy Narx', key: 'oy_narx', width: 12 },
      { header: 'Yil Narx', key: 'yil_narx', width: 12 },
      { header: 'Cheksiz', key: 'cheksiz_narx', width: 12 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    botsSheet.getRow(1).font = { bold: true };
    botsSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4F81BD' },
    };
    botsSheet.getRow(1).alignment = { horizontal: 'center' };

    const botsResult = await query(
      'SELECT * FROM client_bots ORDER BY created_at DESC'
    );

    botsResult.rows.forEach((bot) => {
      botsSheet.addRow({
        ...bot,
        oy_narx: parseFloat(bot.oy_narx) || 0,
        yil_narx: parseFloat(bot.yil_narx) || 0,
        cheksiz_narx: parseFloat(bot.cheksiz_narx) || 0,
        created_at: bot.created_at
          ? new Date(bot.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    // ====== USERS SHEET ======
    const usersSheet = workbook.addWorksheet('Users');
    usersSheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'User ID', key: 'user_id', width: 15 },
      { header: 'Username', key: 'username', width: 20 },
      { header: 'Name', key: 'name', width: 20 },
      { header: 'Duration', key: 'duration', width: 15 },
      { header: 'Balance', key: 'balance', width: 12 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Admin ID', key: 'admin_id', width: 15 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    usersSheet.getRow(1).font = { bold: true };
    usersSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4F81BD' },
    };
    usersSheet.getRow(1).alignment = { horizontal: 'center' };

    const usersResult = await query(
      'SELECT * FROM users ORDER BY created_at DESC'
    );

    usersResult.rows.forEach((user) => {
      usersSheet.addRow({
        ...user,
        balance: parseFloat(user.balance) || 0,
        created_at: user.created_at
          ? new Date(user.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    // ====== TRANSACTIONS SHEET ======
    const transactionsSheet = workbook.addWorksheet('Transactions');
    transactionsSheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'Admin ID', key: 'admin_id', width: 15 },
      { header: 'User ID', key: 'user_id', width: 15 },
      { header: 'Username', key: 'username', width: 20 },
      { header: 'Amount', key: 'amount', width: 15 },
      { header: 'Role', key: 'role', width: 20 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    transactionsSheet.getRow(1).font = { bold: true };
    transactionsSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4F81BD' },
    };
    transactionsSheet.getRow(1).alignment = { horizontal: 'center' };

    const transactionsResult = await query(
      'SELECT * FROM transactions ORDER BY created_at DESC'
    );

    transactionsResult.rows.forEach((trans) => {
      transactionsSheet.addRow({
        ...trans,
        amount: parseFloat(trans.amount) || 0,
        created_at: trans.created_at
          ? new Date(trans.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    // Generate Excel file
    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=system_data_${new Date().toISOString().split('T')[0]}.xlsx`
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export data',
      message: error.message,
    });
  }
});

// Export clients only
router.get('/clients', async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Clients');

    sheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'User ID', key: 'user_id', width: 15 },
      { header: 'Username', key: 'username', width: 20 },
      { header: 'Phone', key: 'phone_number', width: 15 },
      { header: 'Balance', key: 'balance', width: 15 },
      { header: 'Plan', key: 'plan_type', width: 12 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    sheet.getRow(1).font = { bold: true };
    sheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4F81BD' },
    };

    const result = await query('SELECT * FROM clients ORDER BY created_at DESC');

    result.rows.forEach((client) => {
      sheet.addRow({
        ...client,
        balance: parseFloat(client.balance) || 0,
        created_at: client.created_at
          ? new Date(client.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=clients_${new Date().toISOString().split('T')[0]}.xlsx`
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error exporting clients:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export clients',
      message: error.message,
    });
  }
});

// Export transactions only
router.get('/transactions', async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Transactions');

    sheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'Admin ID', key: 'admin_id', width: 15 },
      { header: 'User ID', key: 'user_id', width: 15 },
      { header: 'Username', key: 'username', width: 20 },
      { header: 'Amount', key: 'amount', width: 15 },
      { header: 'Role', key: 'role', width: 20 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    sheet.getRow(1).font = { bold: true };
    sheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4F81BD' },
    };

    const result = await query(
      'SELECT * FROM transactions ORDER BY created_at DESC'
    );

    result.rows.forEach((trans) => {
      sheet.addRow({
        ...trans,
        amount: parseFloat(trans.amount) || 0,
        created_at: trans.created_at
          ? new Date(trans.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=transactions_${new Date().toISOString().split('T')[0]}.xlsx`
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error exporting transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export transactions',
      message: error.message,
    });
  }
});

// Export users only
router.get('/users', async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Users');

    sheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'User ID', key: 'user_id', width: 15 },
      { header: 'Admin ID', key: 'admin_id', width: 15 },
      { header: 'Username', key: 'username', width: 20 },
      { header: 'Name', key: 'name', width: 25 },
      { header: 'Duration', key: 'duration', width: 15 },
      { header: 'Balance', key: 'balance', width: 15 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Invite Link', key: 'invite_link', width: 30 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    sheet.getRow(1).font = { bold: true };
    sheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF9C27B0' },
    };

    const result = await query('SELECT * FROM users ORDER BY created_at DESC');

    result.rows.forEach((user) => {
      sheet.addRow({
        ...user,
        balance: parseFloat(user.balance) || 0,
        created_at: user.created_at
          ? new Date(user.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=users_${new Date().toISOString().split('T')[0]}.xlsx`
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error exporting users:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export users',
      message: error.message,
    });
  }
});

// Export bots only
router.get('/bots', async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Bots');

    sheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'Owner ID', key: 'user_id', width: 15 },
      { header: 'Bot Name', key: 'bot_name', width: 25 },
      { header: 'Bot Username', key: 'bot_username', width: 20 },
      { header: 'Channel ID', key: 'channel_id', width: 15 },
      { header: 'Card Number', key: 'card_number', width: 20 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Process ID', key: 'process_id', width: 12 },
      { header: 'Oy Narx', key: 'oy_narx', width: 15 },
      { header: 'Yil Narx', key: 'yil_narx', width: 15 },
      { header: 'Cheksiz Narx', key: 'cheksiz_narx', width: 15 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    sheet.getRow(1).font = { bold: true };
    sheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF2196F3' },
    };

    const result = await query('SELECT * FROM client_bots ORDER BY created_at DESC');

    result.rows.forEach((bot) => {
      sheet.addRow({
        ...bot,
        oy_narx: parseFloat(bot.oy_narx) || 0,
        yil_narx: parseFloat(bot.yil_narx) || 0,
        cheksiz_narx: parseFloat(bot.cheksiz_narx) || 0,
        created_at: bot.created_at
          ? new Date(bot.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=bots_${new Date().toISOString().split('T')[0]}.xlsx`
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error exporting bots:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export bots',
      message: error.message,
    });
  }
});

// Export deleted bots only
router.get('/deleted-bots', async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Deleted Bots');

    sheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'Original Bot ID', key: 'original_bot_id', width: 15 },
      { header: 'Owner ID', key: 'user_id', width: 15 },
      { header: 'Bot Name', key: 'bot_name', width: 25 },
      { header: 'Bot Username', key: 'bot_username', width: 20 },
      { header: 'Channel ID', key: 'channel_id', width: 15 },
      { header: 'Card Number', key: 'card_number', width: 20 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Users Count', key: 'registered_users_count', width: 12 },
      { header: 'Oy Narx', key: 'oy_narx', width: 15 },
      { header: 'Yil Narx', key: 'yil_narx', width: 15 },
      { header: 'Cheksiz Narx', key: 'cheksiz_narx', width: 15 },
      { header: 'Bot Created At', key: 'bot_created_at', width: 20 },
      { header: 'Deleted At', key: 'deleted_at', width: 20 },
      { header: 'Deletion Reason', key: 'deletion_reason', width: 30 },
    ];

    sheet.getRow(1).font = { bold: true };
    sheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFF44336' },
    };

    const result = await query('SELECT * FROM deleted_bots ORDER BY deleted_at DESC');

    result.rows.forEach((bot) => {
      sheet.addRow({
        ...bot,
        oy_narx: parseFloat(bot.oy_narx) || 0,
        yil_narx: parseFloat(bot.yil_narx) || 0,
        cheksiz_narx: parseFloat(bot.cheksiz_narx) || 0,
        bot_created_at: bot.bot_created_at
          ? new Date(bot.bot_created_at).toLocaleString('uz-UZ')
          : 'N/A',
        deleted_at: bot.deleted_at
          ? new Date(bot.deleted_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=deleted_bots_${new Date().toISOString().split('T')[0]}.xlsx`
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error exporting deleted bots:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export deleted bots',
      message: error.message,
    });
  }
});

// Export spendings only
router.get('/spendings', async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Spendings');

    sheet.columns = [
      { header: 'ID', key: 'id', width: 10 },
      { header: 'User ID', key: 'user_id', width: 15 },
      { header: 'Username', key: 'username', width: 20 },
      { header: 'Amount', key: 'amount', width: 15 },
      { header: 'Spend Type', key: 'spend', width: 20 },
      { header: 'Created At', key: 'created_at', width: 20 },
    ];

    sheet.getRow(1).font = { bold: true };
    sheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFFF9800' },
    };

    const result = await query('SELECT * FROM spendings ORDER BY created_at DESC');

    result.rows.forEach((spending) => {
      sheet.addRow({
        ...spending,
        amount: parseFloat(spending.amount) || 0,
        created_at: spending.created_at
          ? new Date(spending.created_at).toLocaleString('uz-UZ')
          : 'N/A',
      });
    });

    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=spendings_${new Date().toISOString().split('T')[0]}.xlsx`
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error exporting spendings:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export spendings',
      message: error.message,
    });
  }
});

export default router;
