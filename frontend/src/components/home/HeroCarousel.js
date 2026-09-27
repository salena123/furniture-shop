import { useState } from 'react';
import { slides } from '../../config/slides';
export function HeroCarousel({ onEnquiry }) {
  const [slide, setSlide] = useState(0);
  const current = slides[slide];
  return (
    <section
      className="carousel home-carousel"
      aria-label="Карусель кухонь"
      aria-roledescription="карусель"
    >
      <img
        className={`hero-photo hero-photo--${slide + 1}`}
        src={current.image}
        alt={`Фотография кухни ${slide + 1}`}
      />
      <div className="hero-shade" />
      <div className="hero-copy">
        <div aria-live="polite" aria-atomic="true">
          <h1>{current.title}</h1>
          <p>{current.caption}</p>
        </div>
        <button className="enquiry-button" onClick={() => onEnquiry()}>
          Оставить заявку
        </button>
      </div>
      <button
        className="carousel-arrow previous"
        aria-label="Предыдущий слайд"
        onClick={() => setSlide((value) => (value + slides.length - 1) % slides.length)}
      >
        <svg viewBox="0 0 28 28" aria-hidden="true">
          <path d="M21 4 5 14l16 10" />
        </svg>
      </button>
      <button
        className="carousel-arrow next"
        aria-label="Следующий слайд"
        onClick={() => setSlide((value) => (value + 1) % slides.length)}
      >
        <svg viewBox="0 0 28 28" aria-hidden="true">
          <path d="m7 4 16 10L7 24" />
        </svg>
      </button>
      <div className="carousel-dots" role="group" aria-label="Выбор слайда">
        {slides.map((item, index) => (
          <button
            key={item.image}
            aria-label={`Слайд ${index + 1}: ${item.title}`}
            aria-pressed={slide === index}
            onClick={() => setSlide(index)}
          >
            <span />
          </button>
        ))}
      </div>
    </section>
  );
}
