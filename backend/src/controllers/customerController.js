const Customer = require('../models/Customer');
const { createAuditLog } = require('../utils/auditService');
const { createNotification } = require('../utils/notificationService');

// @desc    Get all customers
// @route   GET /api/customers
// @access  Private
const getCustomers = async (req, res) => {
    try {
        const { page = 1, limit = 20, search, status } = req.query;
        const query = {};

        if (search) {
            query.$or = [
                { name: { $regex: search, $options: 'i' } },
                { email: { $regex: search, $options: 'i' } },
                { company: { $regex: search, $options: 'i' } }
            ];
        }

        if (status) {
            query.status = status;
        }

        const customers = await Customer.find(query)
            .limit(limit * 1)
            .skip((page - 1) * limit)
            .sort({ createdAt: -1 })
            .populate('assignedTo', 'firstName lastName email avatar');

        const total = await Customer.countDocuments(query);

        res.json({
            customers,
            totalPages: Math.ceil(total / limit),
            currentPage: page
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Get single customer
// @route   GET /api/customers/:id
// @access  Private
const getCustomer = async (req, res) => {
    try {
        const customer = await Customer.findById(req.params.id)
            .populate('assignedTo', 'firstName lastName email avatar')
            .populate('createdBy', 'firstName lastName');

        if (!customer) {
            return res.status(404).json({ message: 'Customer not found' });
        }

        res.json(customer);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Create a customer
// @route   POST /api/customers
// @access  Private
const createCustomer = async (req, res) => {
    try {
        const customer = await Customer.create({
            ...req.body,
            createdBy: req.user.id
        });

        const populatedCustomer = await Customer.findById(customer._id)
            .populate('assignedTo', 'firstName lastName email avatar');

        await createAuditLog({
            action: 'CREATE',
            entity: 'Customer',
            entityId: customer._id,
            userId: req.user.id,
            req
        });

        // Notify assigned user
        if (customer.assignedTo) {
            await createNotification(req.app.get('io'), {
                userId: customer.assignedTo,
                type: 'CUSTOMER_ASSIGNED',
                title: 'New Customer Assigned',
                message: `You have been assigned customer: ${customer.name}`,
                metadata: { customerId: customer._id }
            });
        }

        req.app.get('io').emit('customer_created', populatedCustomer);

        res.status(201).json(populatedCustomer);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Update customer
// @route   PATCH /api/customers/:id
// @access  Private
const updateCustomer = async (req, res) => {
    try {
        const customer = await Customer.findByIdAndUpdate(
            req.params.id,
            req.body,
            { new: true }
        ).populate('assignedTo', 'firstName lastName email avatar');

        if (!customer) {
            return res.status(404).json({ message: 'Customer not found' });
        }

        await createAuditLog({
            action: 'UPDATE',
            entity: 'Customer',
            entityId: customer._id,
            userId: req.user.id,
            changes: req.body,
            req
        });

        req.app.get('io').emit('customer_updated', customer);

        res.json(customer);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

// @desc    Delete customer
// @route   DELETE /api/customers/:id
// @access  Private (Admin/Manager)
const deleteCustomer = async (req, res) => {
    try {
        if (req.user.role !== 'ADMIN' && req.user.role !== 'MANAGER') {
            return res.status(403).json({ message: 'Insufficient permissions' });
        }

        const customer = await Customer.findByIdAndDelete(req.params.id);

        if (!customer) {
            return res.status(404).json({ message: 'Customer not found' });
        }

        await createAuditLog({
            action: 'DELETE',
            entity: 'Customer',
            entityId: req.params.id,
            userId: req.user.id,
            req
        });

        req.app.get('io').emit('customer_deleted', { id: req.params.id });

        res.json({ message: 'Customer deleted successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

module.exports = {
    getCustomers,
    getCustomer,
    createCustomer,
    updateCustomer,
    deleteCustomer
};
