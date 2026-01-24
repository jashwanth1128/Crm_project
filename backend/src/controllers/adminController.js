const AuditLog = require('../models/AuditLog');

// @desc    Get audit logs
// @route   GET /api/admin/audit-logs
// @access  Private (Admin)
const getAuditLogs = async (req, res) => {
    try {
        const { page = 1, limit = 50, entity, userId } = req.query;
        const query = {};

        if (entity) query.entity = entity;
        if (userId) query.userId = userId;

        const logs = await AuditLog.find(query)
            .limit(limit * 1)
            .skip((page - 1) * limit)
            .sort({ createdAt: -1 })
            .populate('userId', 'firstName lastName email');

        const total = await AuditLog.countDocuments(query);

        res.json({
            logs,
            totalPages: Math.ceil(total / limit),
            currentPage: page
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

module.exports = { getAuditLogs };
