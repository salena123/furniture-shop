import { SiteFooter } from '../components/layout/SiteFooter';
import { SiteHeader } from '../components/layout/SiteHeader';
import { useState, useEffect } from 'react';
import { useResource } from '../hooks/useResource';
import { useAuth } from '../context/AuthContext';
import StaffPages from './StaffPages';
import { ErrorNotice, EmptyState } from '../components/common/Feedback';
import { LoginPage } from '../pages/public/LoginPage';
import HomePage from '../pages/public/HomePage';
import { CatalogPage } from '../pages/public/CatalogPage';
import { ProductPage } from '../pages/public/ProductPage';
import { InfoPage } from '../pages/public/InfoPage';
import CatalogMenu from '../components/catalog/CatalogMenu';
import { EnquiryDialog } from '../components/enquiry/EnquiryDialog';
export function Site() {
  const [route, setRoute] = useState(() => window.location.hash || '#/');
  const [pathname, search = ''] = route.split('?');
  const [enquiry, setEnquiry] = useState(null);
  const options = useResource('/api/catalog/options');
  const auth = useAuth();
  const staff = route.startsWith('#/staff');
  const onEnquiry = (product) =>
    setEnquiry({
      product,
    });
  useEffect(() => {
    let previousPath = (window.location.hash || '#/').split('?')[0];
    const navigate = () => {
      const next = window.location.hash || '#/';
      setRoute(next);
      setEnquiry(null);
      if (next.split('?')[0] !== previousPath) window.scrollTo(0, 0);
      previousPath = next.split('?')[0];
    };
    window.addEventListener('hashchange', navigate);
    return () => window.removeEventListener('hashchange', navigate);
  }, []);
  useEffect(() => {
    document.title = `${staff ? 'Личный кабинет' : route.startsWith('#/catalog') ? 'Каталог мебели' : route === '#/contacts' ? 'Контакты' : route === '#/about' ? 'О нас' : 'Мебель на заказ Нижний Тагил'} – Маэстро`;
  }, [route, staff]);
  let page;
  if (staff) {
    if (auth.checking)
      page = (
        <p className="loading-state" role="status">
          Проверяем вход…
        </p>
      );
    else if (auth.user) page = <StaffPages route={route} onCatalogChanged={options.reload} />;
    else
      page = (
        <>
          <ErrorNotice message={auth.error} onRetry={auth.refresh} />
          <LoginPage />
        </>
      );
  } else if (route === '#/') page = <HomePage onEnquiry={onEnquiry} />;
  else if (/^#\/catalog(?:\/\d+)?$/.test(pathname))
    page = (
      <CatalogPage
        key={pathname}
        categoryId={pathname.split('/')[2]}
        searchParams={search}
        options={options}
      />
    );
  else if (/^#\/product\/\d+$/.test(pathname))
    page = (
      <ProductPage
        key={pathname}
        id={pathname.split('/')[2]}
        searchParams={search}
        options={options}
        onEnquiry={onEnquiry}
      />
    );
  else if (route === '#/about' || route === '#/contacts')
    page = <InfoPage key={route} type={route.slice(2)} onEnquiry={onEnquiry} />;
  else if (route === '#/login')
    page = auth.user ? (
      <EmptyState title="Вы уже вошли">
        <a className="button primary" href="#/staff">
          Перейти в кабинет
        </a>
      </EmptyState>
    ) : (
      <LoginPage />
    );
  else
    page = (
      <EmptyState title="Страница не найдена">
        <a href="#/">Вернуться на главную</a>
      </EmptyState>
    );
  return (
    <div className="site-shell">
      <a
        className="skip-link"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById('main-content')?.focus();
        }}
      >
        К содержимому
      </a>
      <SiteHeader user={auth.user} />
      <main id="main-content" tabIndex="-1">
        {!staff && <CatalogMenu resource={options} route={route} />}
        {page}
      </main>
      {!staff && <SiteFooter />}
      {enquiry && (
        <EnquiryDialog
          product={enquiry.product}
          options={options}
          onClose={() => setEnquiry(null)}
        />
      )}
    </div>
  );
}
