export const contacts = {
  phone: process.env.REACT_APP_CONTACT_PHONE,
  address: process.env.REACT_APP_CONTACT_ADDRESS,
  hours: process.env.REACT_APP_CONTACT_HOURS,
  email: process.env.REACT_APP_CONTACT_EMAIL,
};

// Старые настройки .env действуют только до первого сохранения в админке.
export function resolveContacts(data) {
  return data?.configured ? data : contacts;
}
