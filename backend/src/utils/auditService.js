const AuditLog = require('../models/AuditLog');

const createAuditLog = async ({ action, entity, entityId, userId, changes, req }) => {
    try {
        await AuditLog.create({
            action,
            entity,
            entityId,
            userId,
            changes,
            ipAddress: req?.ip,
            userAgent: req?.get('User-Agent')
        });
    } catch (error) {
        console.error('Error creating audit log:', error);
    }
};

module.exports = { createAuditLog };
