const Activity = require('../models/Activity');
const { createAuditLog } = require('../utils/auditService');

// @desc    Get activities
// @route   GET /api/activities
// @access  Private
const getActivities = async (req, res) => {
    try {
        const { customer_id, lead_id, page = 1, limit = 50 } = req.query;
        const query = {};

        if (customer_id) query.customerId = customer_id;
        if (lead_id) query.leadId = lead_id;

        const activities = await Activity.find(query)
            .limit(limit * 1)
            .skip((page - 1) * limit)
            .sort({ createdAt: -1 })
            .populate('userId', 'firstName lastName avatar');

        res.json(activities);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Create activity
// @route   POST /api/activities
// @access  Private
const createActivity = async (req, res) => {
    try {
        const activity = await Activity.create({
            ...req.body,
            userId: req.user.id
        });

        const populatedActivity = await Activity.findById(activity._id)
            .populate('userId', 'firstName lastName avatar');

        await createAuditLog({
            action: 'CREATE',
            entity: 'Activity',
            entityId: activity._id,
            userId: req.user.id,
            req
        });

        req.app.get('io').emit('activity_created', populatedActivity);

        res.status(201).json(populatedActivity);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Delete activity
// @route   DELETE /api/activities/:id
// @access  Private
const deleteActivity = async (req, res) => {
    try {
        const activity = await Activity.findById(req.params.id);

        if (!activity) {
            return res.status(404).json({ message: 'Activity not found' });
        }

        // Only creator or admin can delete
        if (activity.userId.toString() !== req.user.id && req.user.role !== 'ADMIN') {
            return res.status(403).json({ message: 'Insufficient permissions' });
        }

        await activity.deleteOne();

        await createAuditLog({
            action: 'DELETE',
            entity: 'Activity',
            entityId: req.params.id,
            userId: req.user.id,
            req
        });

        req.app.get('io').emit('activity_deleted', { id: req.params.id });

        res.json({ message: 'Activity deleted successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

module.exports = {
    getActivities,
    createActivity,
    deleteActivity
};
