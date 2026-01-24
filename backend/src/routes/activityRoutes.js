const express = require('express');
const router = express.Router();
const {
    getActivities,
    createActivity,
    deleteActivity
} = require('../controllers/activityController');
const { protect } = require('../middleware/authMiddleware');

router.use(protect);

router.route('/')
    .get(getActivities)
    .post(createActivity);

router.route('/:id')
    .delete(deleteActivity);

module.exports = router;
