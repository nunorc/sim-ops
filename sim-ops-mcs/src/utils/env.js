
export default function getEnv(name, default_) {
  return (window?.configs?.[name] ||  default_)
}

