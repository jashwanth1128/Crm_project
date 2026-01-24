const express = require('express');
const router = express.Router();
const {
    getLeads,
    getLead,
    createLead,
    updateLead,
    deleteLead,
    getLeadStats
} = require('../controllers/leadController');
const { protect } = require('../middleware/authMiddleware');

router.use(protect);

router.get('/stats/overview', getLeadStats); // Must be before /:id to avoid conflict

router.route('/')
    .get(getLeads)
    .post(createLead);

router.route('/:id')
    .get(getLead)
    .patch(updateLead)
    .delete(deleteLead);

module.exports = router;
