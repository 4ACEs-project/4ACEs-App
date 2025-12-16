import React from 'react';
import LandingPage from './LandingPage';
import LanguagePage from './LanguagePage';
import Game from './Game';

const useTranslations = (lang) => {
  const [translations, setTranslations] = React.useState({});
  const [isLoaded, setIsLoaded] = React.useState(false);

  React.useEffect(() => {
    setIsLoaded(false);
    fetch(`/static/locales/${lang}.json?v=${Date.now()}`)
      .then(res => res.json())
      .then(data => {
        setTranslations(data);
        setIsLoaded(true);
      })
      .catch(() => {
        // Fallback to English if the language file is not found
        fetch(`/static/locales/en.json?v=${Date.now()}`)
          .then(res => res.json())
          .then(data => {
            setTranslations(data);
            setIsLoaded(true);
          });
      });
  }, [lang]);

  const t = (key) => {
    return translations[key] || key;
  };

  return { t, isLoaded };
};

const App = () => {
  const [path, setPath] = React.useState(window.location.pathname);
  const [currentLang, setCurrentLang] = React.useState(null);

  React.useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const langFromUrl = urlParams.get('lang');
    if (langFromUrl) {
      fetch(`/api/set_lang/${langFromUrl}`);
      setCurrentLang(langFromUrl);
    } else {
      fetch('/api/get_lang')
        .then(res => res.json())
        .then(data => {
          setCurrentLang(data.lang);
        });
    }
  }, []);

  // Update path when URL changes (for back/forward buttons)
  React.useEffect(() => {
    const handlePopState = () => {
      setPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (newPath) => {
    window.history.pushState({}, '', newPath);
    setPath(newPath);
  };

  // Use currentLang for translations once it's loaded
  const lang = currentLang || 'en'; // Default to 'en' while loading or if backend doesn't provide
  const { t, isLoaded } = useTranslations(lang);

  if (currentLang === null || !isLoaded) {
    return <div>Loading language...</div>; // Show loading state while fetching language
  }

  let Component;
  const currentPath = path.split('?')[0];
  if (currentPath === '/') {
    Component = LandingPage;
  } else if (currentPath === '/language') {
    Component = LanguagePage;
  } else if (currentPath === '/game') {
    Component = Game;
  } else {
    Component = () => <h1>404 Not Found</h1>;
  }

  return (
    <div className="app-container">
      <header>
        <img src="/static/4ACEs_logo.svg" alt="4ACEs logo" />
        <h1>{t('title')}</h1>
      </header>
      <Component navigate={navigate} t={t} lang={lang} setLang={setCurrentLang} isLoaded={isLoaded} />
    </div>
  );
};

export default App;