"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { z } from "zod";
import { AuthCard } from "@/components/auth/AuthCard";
import { Button } from "@/components/ui/Button";
import { TextInput } from "@/components/ui/TextInput";
import { authService } from "@/lib/auth";

const schema = z
  .object({
    currentPassword: z.string().min(1, "Current password is required"),
    newPassword: z.string().min(10, "Password must be at least 10 characters"),
    confirmPassword: z.string().min(1, "Confirm your password"),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords must match",
    path: ["confirmPassword"],
  });

export default function ForcePasswordChangePage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setFieldErrors({});

    const formData = new FormData(event.currentTarget);
    const result = schema.safeParse({
      currentPassword: formData.get("currentPassword"),
      newPassword: formData.get("newPassword"),
      confirmPassword: formData.get("confirmPassword"),
    });

    if (!result.success) {
      setFieldErrors(Object.fromEntries(result.error.issues.map((issue) => [issue.path[0], issue.message])));
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.forcePasswordChange({
        currentPassword: result.data.currentPassword,
        newPassword: result.data.newPassword,
      });
      router.push("/dashboard");
      router.refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to change password");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthCard subtitle="Set a permanent password before entering the dashboard." title="Change temporary password">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <TextInput
          error={fieldErrors.currentPassword}
          label="Current password"
          name="currentPassword"
          type="password"
        />
        <TextInput error={fieldErrors.newPassword} label="New password" name="newPassword" type="password" />
        <TextInput error={fieldErrors.confirmPassword} label="Confirm password" name="confirmPassword" type="password" />
        {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <Button className="w-full" isLoading={isSubmitting} type="submit">
          Change password
        </Button>
      </form>
    </AuthCard>
  );
}

