import React from 'react';

const LandingPage = ({ navigate, t, lang }) => {
  const [highscore, setHighscore] = React.useState('N/A');

  React.useEffect(() => {
    fetch('/api/highscore')
      .then(r => r.json())
      .then(data => {
        setHighscore(data.highscore);
      })
      .catch(() => {
        setHighscore('N/A');
      });
  }, []);

  const flag = lang === 'en' ? 'us' : lang;

  return (
    <div className="content">
      <h2>{t('welcome')}</h2>
      <p>{t('highscore')} {highscore}</p>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '10px' }}>
        <img src={`/static/langs/${flag}.svg`} alt={`${lang} flag`} style={{ height: '48px', marginRight: '10px', border: '1px solid #ccc', cursor: 'pointer' }} onClick={() => navigate('/language')} />
        <button className="modern-btn" onClick={() => navigate(`/game?lang=${lang}`)}>{t('start_new_game')}</button>
      </div>
    </div>
  );
};

export default LandingPage;
