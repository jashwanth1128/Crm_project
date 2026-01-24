const Lead = require('../models/Lead');
const { createAuditLog } = require('../utils/auditService');
const { createNotification } = require('../utils/notificationService');

// @desc    Get all leads
// @route   GET /api/leads
// @access  Private
const getLeads = async (req, res) => {
    try {
        const { page = 1, limit = 100, search, status } = req.query;
        const query = {};

        if (search) {
            query.$or = [
                { title: { $regex: search, $options: 'i' } },
                { description: { $regex: search, $options: 'i' } }
            ];
        }

        if (status) {
            query.status = status;
        }

        const leads = await Lead.find(query)
            .limit(limit * 1)
            .skip((page - 1) * limit)
            .sort({ createdAt: -1 })
            .populate('assignedTo', 'firstName lastName email avatar')
            .populate('customerId', 'name company');

        const total = await Lead.countDocuments(query);

        res.json(leads); // Matches python response structure (just list, not paginated object wrapper, but wait... python code returned just list. I should check if frontend handles pagination. The python code pagination WAS simple list return. I will keep it simple list or check if frontend needs wrapper. To be safe, I will stick to what Python returned which was List[Lead]. But for pagination usually we want count. Let's see python code: `return leads`. Okay, I'll return leads directly for now, but adding headers or metadata is better. I'll stick to array to avoid breaking frontend.)
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Get single lead
// @route   GET /api/leads/:id
// @access  Private
const getLead = async (req, res) => {
    try {
        const lead = await Lead.findById(req.params.id)
            .populate('assignedTo', 'firstName lastName email avatar')
            .populate('customerId', 'name company')
            .populate('createdBy', 'firstName lastName');

        if (!lead) {
            return res.status(404).json({ message: 'Lead not found' });
        }

        res.json(lead);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Create a lead
// @route   POST /api/leads
// @access  Private
const createLead = async (req, res) => {
    try {
        const lead = await Lead.create({
            ...req.body,
            createdBy: req.user.id
        });

        const populatedLead = await Lead.findById(lead._id)
            .populate('assignedTo', 'firstName lastName email avatar')
            .populate('customerId', 'name company');

        await createAuditLog({
            action: 'CREATE',
            entity: 'Lead',
            entityId: lead._id,
            userId: req.user.id,
            req
        });

        // Notify assigned user
        if (lead.assignedTo) {
            await createNotification(req.app.get('io'), {
                userId: lead.assignedTo,
                type: 'LEAD_ASSIGNED',
                title: 'New Lead Assigned',
                message: `You have been assigned lead: ${lead.title}`,
                metadata: { leadId: lead._id }
            });
        }

        req.app.get('io').emit('lead_created', populatedLead);

        res.status(201).json(populatedLead);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Update lead
// @route   PATCH /api/leads/:id
// @access  Private
const updateLead = async (req, res) => {
    try {
        const updates = { ...req.body };

        // If status changed to CONVERTED, set convertedAt
        if (updates.status === 'CONVERTED') {
            updates.convertedAt = Date.now();
        }

        const lead = await Lead.findByIdAndUpdate(
            req.params.id,
            updates,
            { new: true }
        )
            .populate('assignedTo', 'firstName lastName email avatar')
            .populate('customerId', 'name company');

        if (!lead) {
            return res.status(404).json({ message: 'Lead not found' });
        }

        await createAuditLog({
            action: 'UPDATE',
            entity: 'Lead',
            entityId: lead._id,
            userId: req.user.id,
            changes: req.body,
            req
        });

        // Notify if status changed and assigned user exists
        if (req.body.status && lead.assignedTo && lead.assignedTo._id.toString() !== req.user.id) {
            await createNotification(req.app.get('io'), {
                userId: lead.assignedTo._id,
                type: 'LEAD_UPDATED',
                title: 'Lead Status Updated',
                message: `Lead '${lead.title}' status changed to ${req.body.status}`,
                metadata: { leadId: lead._id }
            });
        }

        req.app.get('io').emit('lead_updated', lead);

        res.json(lead);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Delete lead
// @route   DELETE /api/leads/:id
// @access  Private (Admin/Manager)
const deleteLead = async (req, res) => {
    try {
        if (req.user.role !== 'ADMIN' && req.user.role !== 'MANAGER') {
            return res.status(403).json({ message: 'Insufficient permissions' });
        }

        const lead = await Lead.findByIdAndDelete(req.params.id);

        if (!lead) {
            return res.status(404).json({ message: 'Lead not found' });
        }

        await createAuditLog({
            action: 'DELETE',
            entity: 'Lead',
            entityId: req.params.id,
            userId: req.user.id,
            req
        });

        req.app.get('io').emit('lead_deleted', { id: req.params.id });

        res.json({ message: 'Lead deleted successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Get lead stats
// @route   GET /api/leads/stats/overview
// @access  Private
const getLeadStats = async (req, res) => {
    try {
        const stats = await Lead.aggregate([
            {
                $group: {
                    _id: "$status",
                    count: { $sum: 1 },
                    total_value: { $sum: "$value" }
                }
            }
        ]);
        res.json({ stats });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

module.exports = {
    getLeads,
    getLead,
    createLead,
    updateLead,
    deleteLead,
    getLeadStats
};
