# Phase 12: Learning Center

**Goal**: Build a structured educational module allowing beginners to learn technical and fundamental concepts (RSI, MACD, P/E ratio, etc.).

## Tasks
1. **T01 - Data Models & Storage**
   - Create EducationalModule and EducationalLesson models.
   - Create UserLessonProgress model to track completions.

2. **T02 - Content Seeding**
   - Seed the database with structured markdown content for Technical (RSI, MACD, SMA) and Fundamental (F/K, PD/DD) concepts.

3. **T03 - API Endpoints**
   - GET /api/v1/education/modules
   - GET /api/v1/education/modules/{id}/lessons
   - POST /api/v1/education/lessons/{id}/complete

4. **T04 - Frontend Integration**
   - Build /education page listing modules.
   - Build /education/[lessonId] page showing markdown content, progress tracking, and a "Complete" button.
