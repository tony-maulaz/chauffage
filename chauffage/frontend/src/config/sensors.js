/**
 * Mapping between dashboard slots (0-11) and Homematic IP device IDs.
 * Update this list to match your real sensors.
 */
const sensors = [
  { num: 10, id: "3014F711A0000E9A499B2975", name: "Cave" },
  { num: 7, id: "3014F711A000265A49A57BAF", name: "Cuisine" },
  { num: 11, id: "3014F711A000265A49A57BBF", name: "Buanderie" },
  { num: 3, id: "3014F711A000265A49A5800E", name: "Parent" },
  { num: 6, id: "3014F711A000265A49A57B63", name: "Salon" },
  { num: 8, id: "3014F711A000265A49A57B73", name: "Hall" },
  { num: 5, id: "3014F711A000265A49A57B5D", name: "Justine" },
  { num: 0, id: "3014F711A000265A49A57BB5", name: "Quentin" },
  { num: 4, id: "3014F711A000265A49A57BA3", name: "Axel" },
  { num: 1, id: "3014F711A0000EDA4995B660", name: "Ext. devant" },
  { num: 2, id: "3014F711A0000EDA4995B675", name: "Ext. côté" },
  { num: 9, id: "3014F711A0000E9A499B2979", name: "Bureau" },
];

export default sensors;
