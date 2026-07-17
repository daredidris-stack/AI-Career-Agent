import { Fragment } from "react";
import { Menu, Transition } from "@headlessui/react";
import {
  ChevronDown,
  User,
  LayoutDashboard,
  Settings,
  Bell,
  CreditCard,
  CircleHelp,
  LogOut,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function UserMenu({
  firstName = "Dare",
  fullName = "User",
  onLogout,
}) {
  const navigate = useNavigate();

  return (
    <Menu
      as="div"
      className="relative"
    >
      <Menu.Button
        className="
          flex
          items-center
          gap-2
          rounded-xl
          px-3
          py-2
          hover:bg-gray-800
          transition
        "
      >
        <div
          className="
            w-9
            h-9
            rounded-full
            bg-blue-600
            flex
            items-center
            justify-center
            text-white
            font-semibold
          "
        >
          {firstName.charAt(0)}
        </div>

        <span className="text-white font-medium">
          {firstName}
        </span>

        <ChevronDown
          size={18}
          className="text-gray-400"
        />
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-150"
        enterFrom="opacity-0 scale-95"
        enterTo="opacity-100 scale-100"
        leave="transition ease-in duration-100"
        leaveFrom="opacity-100 scale-100"
        leaveTo="opacity-0 scale-95"
      >
        <Menu.Items
          className="
            absolute
            right-0
            mt-3
            w-72
            origin-top-right
            rounded-2xl
            border
            border-gray-800
            bg-gray-900
            shadow-2xl
            focus:outline-none
            overflow-hidden
            z-50
          "
        >
          <div className="px-5 py-4 border-b border-gray-800">
            <p className="text-white font-semibold">
              {fullName}
            </p>
          </div>

          <div className="py-2">

            <MenuItem
              icon={<User size={18} />}
              label="My Profile"
              onClick={() => navigate("/profile")}
            />

            <MenuItem
              icon={<LayoutDashboard size={18} />}
              label="Dashboard"
              onClick={() => navigate("/dashboard")}
            />

            <MenuItem
              icon={<Settings size={18} />}
              label="Settings"
              onClick={() => navigate("/settings")}
            />

            <MenuItem
              icon={<Bell size={18} />}
              label="Notifications"
            />

            <MenuItem
              icon={<CreditCard size={18} />}
              label="Billing (Coming Soon)"
              disabled
            />

            <MenuItem
              icon={<CircleHelp size={18} />}
              label="Help Center"
            />

          </div>

          <div className="border-t border-gray-800 py-2">

            <MenuItem
              icon={<LogOut size={18} />}
              label="Sign Out"
              danger
              onClick={onLogout}
            />

          </div>

        </Menu.Items>
      </Transition>
    </Menu>
  );
}

function MenuItem({
  icon,
  label,
  danger,
  disabled,
  onClick,
}) {
  return (
    <Menu.Item disabled={disabled}>
      {({ active }) => (
        <button
          onClick={onClick}
          disabled={disabled}
          className={`
            w-full
            flex
            items-center
            gap-3
            px-5
            py-3
            text-left
            transition

            ${active ? "bg-gray-800" : ""}

            ${danger ? "text-red-400" : "text-gray-200"}

            ${disabled ? "opacity-40 cursor-not-allowed" : ""}
          `}
        >
          {icon}
          {label}
        </button>
      )}
    </Menu.Item>
  );
}
