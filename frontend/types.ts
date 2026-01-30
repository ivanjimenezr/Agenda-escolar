
export interface User {
  name: string;
  email: string;
}

export interface StudentProfile {
  id: string;
  name: string;
  school: string;
  grade: string;
  avatarUrl: string;
  allergies: string[]; // 'gluten', 'lactose'
  excludedFoods: string[];
  activeModules: ActiveModules;
}

export interface Subject {
  id: string;
  studentId: string;
  name: string;
  days: ('Lunes' | 'Martes' | 'Miércoles' | 'Jueves' | 'Viernes')[];
  time: string;
  teacher: string;
  color: string;
  type: 'colegio' | 'extraescolar';
}

export interface Center {
  id: string;
  name: string;
}

export interface Contact {
  id: string;
  centerId: string;
  name: string;
  phone: string;
  role?: string;
}

export interface Exam {
  id: string;
  studentId: string;
  subject: string;
  date: string;
  topic: string;
  notes?: string;
}

export interface MenuItem {
  id: string;
  date: string;
  mainCourse: string;
  sideDish: string;
  dessert: string;
}

export interface DinnerItem {
  id: string;
  studentId: string;
  date: string;
  meal: string;
  ingredients: string[];
}

export interface SchoolEvent {
  id: string;
  date: string;
  name: string;
  type: 'Festivo' | 'Lectivo' | 'Vacaciones';
}

export type View = 'home' | 'dinners' | 'manage' | 'profile';

export type ModuleKey = 'subjects' | 'exams' | 'menu' | 'events' | 'dinner' | 'contacts';

export interface ActiveModules {
  subjects: boolean;
  exams: boolean;
  menu: boolean;
  events: boolean;
  dinner: boolean;
  contacts: boolean;
}

export interface CardOrder {
  order: ModuleKey[];
}
