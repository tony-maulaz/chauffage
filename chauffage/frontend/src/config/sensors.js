/**
 * Mapping between dashboard slots (0-11) and Homematic IP device IDs.
 * Update this list to match your real sensors.
 */
const sensors = [
  { num: 0, id: "3014F711A0000E9A499B2975", name: "Cave" },
  { num: 1, id: "3014F711A000265A49A57BAF", name: "Cuisine" },
  { num: 2, id: "3014F711A000265A49A57BBF", name: "Buanderie" },
  { num: 3, id: "3014F711A000265A49A5800E", name: "Parent" },
  { num: 4, id: "3014F711A000265A49A57B63", name: "Salon" },
  { num: 5, id: "3014F711A000265A49A57B73", name: "Hall" },
  { num: 6, id: "3014F711A000265A49A57B5D", name: "Justine" },
  { num: 7, id: "3014F711A000265A49A57BB5", name: "Quentin" },
  { num: 8, id: "3014F711A000265A49A57BA3", name: "Axel" },
  { num: 9, id: "", name: "Ext. devant" },
  { num: 10, id: "", name: "Ext. côté" },
];

export default sensors;
