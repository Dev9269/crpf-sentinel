"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, UserRound, ShieldCheck } from "lucide-react";
import { userService, unitService } from "@/services";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { PageError, PageLoading, PageEmpty } from "@/components/shared/page-states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatDateTime, cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { ApiError } from "@/lib/api";

export default function UsersPage() {
  const { user: me } = useAuth();
  const queryClient = useQueryClient();
  const [creating, setCreating] = useState(false);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["users"],
    queryFn: () => userService.list(),
  });

  return (
    <div>
      <PageHeader
        title="Users & Access"
        description="Manage platform users, roles, and unit scoping."
        actions={
          <Button size="sm" onClick={() => setCreating(true)}>
            <Plus className="h-3.5 w-3.5" />
            New User
          </Button>
        }
      />

      {isLoading && <PageLoading rows={10} />}
      {isError && <PageError message={(error as Error)?.message} onRetry={() => refetch()} />}
      {data && data.length === 0 && <PageEmpty title="No users found" />}

      {data && data.length > 0 && (
        <div className="rounded-md border border-border bg-surface">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Unit</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Login</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((u) => (
                <TableRow key={u.id} className={cn(!u.is_active && "opacity-50")}>
                  <TableCell>
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full border border-border bg-surface2">
                        <UserRound className="h-4 w-4 text-accent" />
                      </div>
                      <div>
                        <span className="block text-xs font-medium text-foreground">
                          {u.full_name ?? u.username}
                          {u.id === me?.id && <span className="ml-1.5 text-[10px] text-accent">(you)</span>}
                        </span>
                        <span className="block font-mono text-[10px] text-muted">@{u.username} · {u.email}</span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.role?.name === "super_admin" ? "accent" : "outline"} className="text-[9px]">
                      <ShieldCheck className="mr-1 h-3 w-3" />
                      {u.role?.name ?? "—"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted">{u.unit_id ? "Unit scoped" : "Global"}</TableCell>
                  <TableCell>
                    <Badge variant={u.is_active ? "success" : "default"} className="text-[9px]">
                      {u.is_active ? "active" : "inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="whitespace-nowrap font-mono text-[11px] text-muted">{formatDateTime(u.last_login_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {creating && (
        <CreateUserDialog
          onClose={() => setCreating(false)}
          onCreated={() => {
            setCreating(false);
            void queryClient.invalidateQueries({ queryKey: ["users"] });
          }}
        />
      )}
    </div>
  );
}

function CreateUserDialog({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: () => userService.roles() });
  const { data: units } = useQuery({ queryKey: ["units", "all"], queryFn: () => unitService.list() });
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [roleId, setRoleId] = useState("");
  const [unitId, setUnitId] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function create() {
    setError(null);
    setSaving(true);
    try {
      await userService.create({
        username: username.trim(),
        email: email.trim(),
        full_name: fullName.trim() || null,
        password,
        role_id: roleId,
        unit_id: unitId || null,
        is_active: isActive,
      });
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create user");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={onClose}>
      <div className="w-full max-w-md rounded-md border border-border bg-surface p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-base font-semibold text-foreground">Create User</h3>
        <p className="mt-1 text-xs text-muted">The user will be required to change their password on first login.</p>

        {error && <div className="mt-3 rounded-md border border-critical/30 bg-critical/10 px-3 py-2 text-xs text-critical">{error}</div>}

        <div className="mt-4 space-y-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1">
              <Label htmlFor="username">Username</Label>
              <Input id="username" value={username} onChange={(e) => setUsername(e.target.value)} className="font-mono" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="full_name">Full name</Label>
              <Input id="full_name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="password">Temporary password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Role</Label>
              <Select value={roleId} onValueChange={setRoleId}>
                <SelectTrigger><SelectValue placeholder="Select role" /></SelectTrigger>
                <SelectContent>
                  {roles?.map((r) => (
                    <SelectItem key={r.id} value={r.id}>{r.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Unit scope</Label>
              <Select value={unitId} onValueChange={setUnitId}>
                <SelectTrigger><SelectValue placeholder="Global (all units)" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Global (all units)</SelectItem>
                  {units?.map((u) => (
                    <SelectItem key={u.id} value={u.id}>{u.unit_code} · {u.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2 sm:col-span-2">
              <Switch checked={isActive} onCheckedChange={setIsActive} id="active" />
              <Label htmlFor="active">Active account</Label>
            </div>
          </div>
        </div>

        <div className="mt-5 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={() => void create()} disabled={saving || !username.trim() || !password || !roleId}>
            {saving ? "Creating…" : "Create User"}
          </Button>
        </div>
      </div>
    </div>
  );
}
