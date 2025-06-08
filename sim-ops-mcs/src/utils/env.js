
export default function getEnv(name, default_) {
  const _name = `VITE_${name}`
  if (_name in import.meta.env)
    return import.meta.env?.[_name]

  return (window?.configs?.[name] || default_)
}

