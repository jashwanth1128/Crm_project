const express = require('express');
const router = express.Router();
const { getUsers, updateUser } = require('../controllers/userController');
const { protect, admin } = require('../middleware/authMiddleware');

router.use(protect);

router.get('/', getUsers);
router.patch('/:id', updateUser);

module.exports = router;
