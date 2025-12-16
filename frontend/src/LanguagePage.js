import React from 'react';

const LanguagePage = ({ navigate, t, setLang }) => {
  const [languages, setLanguages] = React.useState([]);

  React.useEffect(() => {
    fetch('/api/languages')
      .then(res => res.json())
      .then(data => setLanguages(data))
      .catch(() => setLanguages(['en'])); // Fallback to English
  }, []);

  const handleLanguageSelect = (lang) => {
    fetch(`/api/set_lang/${lang}`)
      .then(() => {
        setLang(lang);
        navigate(`/game?lang=${lang}`); // Go directly to the game
      });
  };

  return (
    <div className="content">
      <h2>{t('choose_your_language')}</h2>
      <div className="lang-options">
        {languages.map(lang => {
          const flag = lang === 'en' ? 'us' : lang;
          return (
            <div onClick={() => handleLanguageSelect(lang)} key={lang} style={{ cursor: 'pointer' }}>
              <img src={`/static/langs/${flag}.svg`} alt={lang} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LanguagePage;
