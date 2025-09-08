# 📝 Online Exam System

<div align="center">

![GitHub](https://img.shields.io/github/license/yourusername/online-exam-system)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-4.x-green.svg)
![React](https://img.shields.io/badge/react-latest-blue.svg)

A modern, secure, and feature-rich online examination platform built with Django REST Framework and React.

[Features](#features) • [Tech Stack](#tech-stack) • [Installation](#installation) • [API Docs](#api-endpoints) • [Contributing](#contributing)

</div>

## ✨ Features

- 👥 **Role-Based Access Control**: Student, Teacher, and Admin roles
- 📝 **Advanced Exam Management**: Create, edit, and manage diverse question types
- ⚡ **Automated Grading System**: Instant scoring and feedback
- 📊 **Real-time Monitoring**: Track progress and results
- 🔐 **Secure Authentication**: JWT-based system
- 📚 **RESTful API**: Clean design with comprehensive documentation

## 🛠️ Technology Stack

### Backend
- Django 4.x + Django REST Framework
- Simple JWT for authentication
- PostgreSQL / SQLite
- DRF Spectacular for API docs

### Frontend (Coming Soon)
- React.js with Redux
- Material-UI
- Axios

## 📦 Project Structure
```
online-exam-system/
├── backend/
│   ├── users/         # User management
│   ├── exams/         # Exam management
│   ├── submissions/   # Submission handling
│   └── exam_system/   # Core settings
├── frontend/          # React app (upcoming)
└── docs/             # Documentation
```

## 🚀 Quick Start

1. **Clone & Setup**
```bash
git clone <repository-url>
cd online-exam-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install & Configure**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

3. **Launch**
```bash
python manage.py runserver
```

Visit:
- API: http://localhost:8000
- Admin: http://localhost:8000/admin
- Docs: http://localhost:8000/api/docs

## 🔑 Core Features

### User Roles
- 👨‍🎓 **Student**: Take exams, view results
- 👨‍🏫 **Teacher**: Create exams, manage questions
- 👨‍💼 **Admin**: Full system control

### Security
- JWT Authentication
- Role-based access
- XSS & CSRF protection
- Input validation

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📬 Contact

Project Link: [https://github.com/kamal2131/online-exam-system](https://github.com/kamal2131/online-exam-system)

---

<div align="center">
⭐ Star us on GitHub — it motivates us a lot!
</div>
