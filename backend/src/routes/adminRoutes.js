const express = require('express');
const router = express.Router();
const { getAuditLogs } = require('../controllers/adminController');
const { protect, admin } = require('../middleware/authMiddleware');

router.use(protect);
router.use(admin); // All admin routes require 'ADMIN' role

router.get('/audit-logs', getAuditLogs);

module.exports = router;
