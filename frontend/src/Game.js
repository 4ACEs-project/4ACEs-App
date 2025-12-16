import React from 'react';

const Game = ({ navigate, t, lang, isLoaded }) => {
  const [round, setRound] = React.useState(0);
  const [score, setScore] = React.useState(0);
  const [symbol, setSymbol] = React.useState(null);
  const [sentence, setSentence] = React.useState(null);
  const [audioUrl, setAudioUrl] = React.useState(null);
  const audioRef = React.useRef(null);
  const [soundEffectUrl, setSoundEffectUrl] = React.useState(null);
  const soundEffectRef = React.useRef(null);
  const [sentenceIndices, setSentenceIndices] = React.useState({});
  const [options, setOptions] = React.useState([]);
  const [correct, setCorrect] = React.useState(null);
  const [answerResult, setAnswerResult] = React.useState(null);
  const [phase, setPhase] = React.useState('loading'); // loading, showSymbol, choose, showResult, finished

  const loadNext = () => {
    fetch('/api/next')
      .then(res => res.json())
      .then(data => {
        if (data.finished) {
          setPhase('finished');
        } else {
          if (lang === 'pl') {
            setSentence(data.sentence);
            const audioFile = `${data.sentence_key}.mp3`;
            const audioPath = `/static/mp3s/${lang}/${audioFile}?v=${Date.now()}`;
            setAudioUrl(audioPath);
          } else {
            setSymbol(data.symbol);
            const sentences = t(`${data.symbol}_sentences`);
            if (Array.isArray(sentences) && sentences.length > 0) {
              const currentIndex = sentenceIndices[data.symbol] || 0;
              setSentence(sentences[currentIndex]);
              const audioFile = `${data.symbol.toLowerCase()}_${currentIndex + 1}.mp3`;
              const audioPath = `/static/mp3s/${lang}/${audioFile}?v=${Date.now()}`;
              setAudioUrl(audioPath);
              setSentenceIndices(prev => ({
                ...prev,
                [data.symbol]: (currentIndex + 1) % sentences.length,
              }));
            } else {
              setSentence(t(data.symbol));
            }
          }
          setOptions(data.options);
          setCorrect(data.correct);
          setPhase('showSymbol');
          // Show the symbol/sentence for 2 seconds, then ask to choose.
          setTimeout(() => setPhase('choose'), 2000);
        }
      })
      .catch(err => console.error('API error', err));
  };

  React.useEffect(() => {
    if (isLoaded) {
      loadNext();
    }
  }, [isLoaded]);

  React.useEffect(() => {
    if (phase === 'showSymbol' && audioRef.current && audioRef.current.src) {
      audioRef.current.play().catch(error => {
        console.error("Audio playback error:", error);
      });
    }
  }, [phase, audioUrl]);

  React.useEffect(() => {
    if (soundEffectUrl && soundEffectRef.current) {
      soundEffectRef.current.play().catch(e => console.error("SFX Error:", e));
    }
  }, [soundEffectUrl]);

  React.useEffect(() => {
    if (phase === 'finished') {
      submitScore();
      playSound('win-sound-effect.mp3');
    }
  }, [phase]);

  const playSound = (soundFile) => {
    setSoundEffectUrl(`/static/mp3s/${soundFile}?v=${Date.now()}`);
  };

  const handleQuit = () => {
    fetch('/api/quit');
    navigate(`/?lang=${lang}`);
  };

  const flag = lang === 'en' ? 'us' : lang;

  const handleChoice = (img) => {
    if (img === correct) {
      setScore(s => s + 1);
      setAnswerResult('correct');
      playSound('correct-ding-gameshow.mp3');
    } else {
      playSound('click-wrong.mp3');
    }
    setPhase('showResult');
    setTimeout(() => {
      setRound(r => r + 1);
      loadNext();
      setAnswerResult(null);
    }, 1000); // Show result for 1 second
  };

  const submitScore = () => {
    fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score })
    })
      .then(r => r.json())
      .catch(() => console.error('Failed to submit score'));
  };

  if (phase === 'loading') return <div>{t('loading')}</div>;
  if (phase === 'finished') {
    return (
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <h3 style={{ fontSize: '1.5em' }}>{t('game_over')} {score} / 10</h3>
        <div style={{ marginTop: '20px' }}>
          <button onClick={() => navigate(`/?lang=${lang}`)} className="modern-btn">{t('back_to_home')}</button>
        </div>
      </div>
    );
  }

  return (
    <div className="game-container">
      <audio ref={audioRef} src={audioUrl} />
      <audio ref={soundEffectRef} src={soundEffectUrl} />
      <div className="game-stats">
        <img src={`/static/langs/${flag}.svg`} alt={`${lang} flag`} className="game-flag" onClick={() => navigate('/language')} />
        <h2>{t('round')} {round + 1} / 10</h2>
        <p>{t('score')} {score}</p>
        <button onClick={handleQuit} className="modern-btn">{t('quit')}</button>
      </div>
      {phase === 'choose' && <p>{t('select_picture_instruction')}</p>}
      <div className="game-area">
        {phase === 'showSymbol' && <h3>{sentence}</h3>}
        {phase === 'choose' && (
          <div className="options">
            {options.map((src, i) => (
              <img
                key={i}
                src={src}
                alt="option"
                className="option-image"
                onClick={() => handleChoice(src)}
              />
            ))}
          </div>
        )}
        {phase === 'showResult' && answerResult === 'correct' && (
          <div style={{ color: 'green', fontSize: '2em', height: '120px', display: 'flex', alignItems: 'center' }}>
            {t('correct')}
          </div>
        )}
      </div>
    </div>
  );
};

export default Game;