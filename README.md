# Advanced Online Quiz System

A comprehensive online quiz platform with an AI-powered chatbot assistant, built using Django and modern web technologies. Now available as a desktop application for easy sharing and offline use.

## Features

### Core Quiz Features
- Multi-user support (Students, Teachers, Administrators)
- Dynamic quiz creation and management
- Real-time quiz taking with timer
- Automatic grading and result analysis
- Course management system
- Performance tracking and statistics

### AI Chatbot Assistant
- Intelligent query handling for quiz-related questions
- Personalized responses based on user role
- Real-time statistics and progress tracking
- Course-specific information
- Technical support and guidance
- Interactive suggestions
- Context-aware responses

### User Management
- Role-based access control
- Student progress tracking
- Teacher dashboard
- Admin control panel
- Secure authentication

### Technical Features
- Modern responsive UI
- Real-time updates
- Mobile-friendly design
- Cross-browser compatibility
- Secure data handling

## Technology Stack

### Backend
- Python 3.7+
- Django 3.2+
- SQLite Database
- Redis for real-time features

### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap for responsive design
- Font Awesome icons
- Custom animations and effects

### Desktop Application
- Electron framework
- Auto-updater support
- Cross-platform compatibility
- Offline database synchronization

### Additional Tools
- Django REST framework
- WebSocket support
- Advanced caching system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/onlinequiz.git
cd onlinequiz
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create admin user:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Main site: http://127.0.0.1:8000
- Admin panel: http://127.0.0.1:8000/admin

## User Roles

### Admin
- Manage all users and content
- Create/modify courses
- Monitor system performance
- Access analytics

### Teacher
- Create and manage quizzes
- Add/edit questions
- View student performance
- Grade submissions
- Generate reports

### Student
- Take quizzes
- View results
- Track progress
- Access study materials
- Get AI chatbot assistance

## AI Chatbot Usage

The AI chatbot provides assistance for:
- Quiz rules and guidelines
- Course information
- Technical support
- Study tips
- Progress tracking
- Schedule management
- Performance statistics

To use the chatbot:
1. Click the chat icon on the right side of any page
2. Type your question or select a suggestion
3. Get instant, context-aware responses
4. Use quick suggestions for common queries

## Security Features

- Secure authentication system
- CSRF protection
- XSS prevention
- Secure session handling
- Input validation
- Role-based access control

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Desktop Application Distribution

### Building the Application

1. Make sure you have Node.js installed
2. Install dependencies:
```bash
npm install
```

3. Build the application:
```bash
npm run build
```

4. Find the installer in the `dist` folder

### Sharing Across Different PCs

#### Option 1: Installer (Recommended)

1. Share the installer file (`Quiz App-1.0.0-win.exe`) with others
2. Recipients should run the installer as administrator
3. The application will be installed with all necessary components

#### Option 2: Portable Version

1. Share the portable version (`Quiz App-Portable-1.0.0.exe`) via USB drive or cloud storage
2. Recipients can run the application directly without installation
3. Data will be stored in the same directory as the application

### Avoiding Antivirus Issues

1. **Code Signing**: For commercial distribution, consider code signing the application
2. **Whitelist the Application**: Add the application to your antivirus whitelist
3. **Run as Administrator**: Always run the application as administrator
4. **Disable SmartScreen**: If using Windows, temporarily disable SmartScreen when installing
5. **Create Exception**: Create an exception in Windows Defender or other antivirus software

### Troubleshooting Common Issues

1. **Application Blocked**: Add to antivirus exceptions or whitelist
2. **Database Errors**: Check if the database file is accessible and not corrupted
3. **Server Not Starting**: Ensure no other application is using port 8000
4. **Updates Failing**: Check internet connection and firewall settings

## Support

For support, email: support@onlinequiz.com

## Acknowledgments

- Django community
- Bootstrap team
- Font Awesome
- Electron framework
- All contributors
