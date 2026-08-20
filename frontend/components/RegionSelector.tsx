export default function RegionSelector() {
  return (
    <div className="flex items-center justify-between border border-hairline bg-surface px-4 py-3 text-sm">
      <span className="text-muted">Zone</span>
      <select disabled className="bg-transparent text-ink outline-none disabled:cursor-not-allowed" defaultValue="toronto">
        <option value="toronto">Toronto</option>
      </select>
    </div>
  );
}