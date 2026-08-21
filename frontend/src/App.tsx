import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/HomePage';
import { StoryDetailPage } from './pages/StoryDetailPage';
import { MyLibraryPage } from './pages/MyLibraryPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/stories/:id" element={<StoryDetailPage />} />
        <Route path="/library" element={<MyLibraryPage />} />
        <Route path="/admin" element={<AdminDashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
