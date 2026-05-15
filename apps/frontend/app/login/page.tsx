"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { z } from "zod";
import { AuthCard } from "@/components/auth/AuthCard";
import { Button } from "@/components/ui/Button";
import { TextInput } from "@/components/ui/TextInput";
import { authService } from "@/lib/auth";

const loginSchema = z.object({
  identifier: z.string().min(1, "Email or username is required"),
  password: z.string().min(1, "Password is required"),
});

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setFieldErrors({});

    const formData = new FormData(event.currentTarget);
    const result = loginSchema.safeParse({
      identifier: formData.get("identifier"),
      password: formData.get("password"),
    });

    if (!result.success) {
      setFieldErrors(Object.fromEntries(result.error.issues.map((issue) => [issue.path[0], issue.message])));
      return;
    }

    setIsSubmitting(true);
    try {
      const user = await authService.login(result.data);
      router.push(user.forcePasswordChange ? "/force-password-change" : "/dashboard");
      router.refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to sign in");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthCard subtitle="Sign in with your staff username or email." title="Sign in to TCMS ERP">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <TextInput error={fieldErrors.identifier} label="Email or username" name="identifier" autoComplete="username" />
        <TextInput
          error={fieldErrors.password}
          label="Password"
          name="password"
          type="password"
          autoComplete="current-password"
        />
        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-slate-600">
            <input className="rounded border-slate-300 text-[#0948B3]" type="checkbox" />
            Remember me
          </label>
          <Link className="font-medium text-[#0948B3] hover:underline" href="/forgot-password">
            Lost password?
          </Link>
        </div>
        {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <Button className="w-full" isLoading={isSubmitting} type="submit">
          Sign in
        </Button>
      </form>
    </AuthCard>
  );
}

