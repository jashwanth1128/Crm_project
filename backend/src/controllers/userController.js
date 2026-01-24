const User = require('../models/User');
const { createAuditLog } = require('../utils/auditService');

// @desc    Get all users
// @route   GET /api/users
// @access  Private
const getUsers = async (req, res) => {
    try {
        const users = await User.find({})
            .select('-password')
            .sort({ createdAt: -1 });
        res.json(users);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Update user
// @route   PATCH /api/users/:id
// @access  Private
const updateUser = async (req, res) => {
    try {
        const user = await User.findById(req.params.id);

        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }

        // Check permissions
        // Admin can update anyone. Users can update themselves (but not role/status).
        const isAdmin = req.user.role === 'ADMIN';
        const isSelf = req.user.id === req.params.id;

        if (!isAdmin && !isSelf) {
            return res.status(403).json({ message: 'Insufficient permissions' });
        }

        // Filter updates based on role
        const updates = { ...req.body };
        delete updates.password; // Handle password change separately if needed, or use specific endpoint
        delete updates.email; // Don't allow email change for now

        if (!isAdmin) {
            delete updates.role;
            delete updates.status;
            delete updates.isVerified;
        }

        const updatedUser = await User.findByIdAndUpdate(
            req.params.id,
            updates,
            { new: true }
        ).select('-password');

        await createAuditLog({
            action: 'UPDATE',
            entity: 'User',
            entityId: user._id,
            userId: req.user.id,
            changes: updates,
            req
        });

        res.json(updatedUser);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

module.exports = {
    getUsers,
    updateUser
};
