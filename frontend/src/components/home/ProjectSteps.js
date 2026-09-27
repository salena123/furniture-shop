const steps = [
  ['Выберите пример', 'Посмотрите наши работы и сохраните идеи для своего интерьера.'],
  ['Расскажите о пожеланиях', 'Укажите размеры, материал, цвет и то, что для вас важно.'],
  ['Обсудите проект', 'Оставьте заявку, чтобы вместе с сотрудником уточнить детали.'],
];
export function ProjectSteps({ onEnquiry }) {
  return (
    <section className="home-process" aria-labelledby="home-process-title">
      <div className="home-section-heading">
        <div>
          <p className="eyebrow">От идеи к вашему проекту</p>
          <h2 id="home-process-title">Начнём с ваших пожеланий</h2>
        </div>
      </div>
      <ol className="home-steps">
        {steps.map(([title, text], index) => (
          <li key={title}>
            <span className="home-step-number" aria-hidden="true">
              0{index + 1}
            </span>
            <h3>{title}</h3>
            <p>{text}</p>
          </li>
        ))}
      </ol>
      <div className="home-process-action">
        <p>Есть идея? Давайте обсудим её вместе.</p>
        <button className="button primary" onClick={() => onEnquiry()}>
          Оставить заявку
        </button>
      </div>
    </section>
  );
}
