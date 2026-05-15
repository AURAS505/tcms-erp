"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { z } from "zod";
import { AuthCard } from "@/components/auth/AuthCard";
import { Button } from "@/components/ui/Button";
import { TextInput } from "@/components/ui/TextInput";
import { authService } from "@/lib/auth";

const schema = z
  .object({
    token: z.string().min(1, "Reset token is required"),
    newPassword: z.string().min(10, "Password must be at least 10 characters"),
    confirmPassword: z.string().min(1, "Confirm your password"),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords must match",
    path: ["confirmPassword"],
  });

export default function ResetPasswordPage() {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setMessage("");
    setFieldErrors({});

    const formData = new FormData(event.currentTarget);
    const result = schema.safeParse({
      token: formData.get("token"),
      newPassword: formData.get("newPassword"),
      confirmPassword: formData.get("confirmPassword"),
    });

    if (!result.success) {
      setFieldErrors(Object.fromEntries(result.error.issues.map((issue) => [issue.path[0], issue.message])));
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.confirmPasswordReset({
        token: result.data.token,
        newPassword: result.data.newPassword,
      });
      setMessage("Password reset complete. You can sign in now.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to reset password");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthCard subtitle="Use the token from your reset email or local debug response." title="Reset password">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <TextInput error={fieldErrors.token} label="Reset token" name="token" />
        <TextInput error={fieldErrors.newPassword} label="New password" name="newPassword" type="password" />
        <TextInput error={fieldErrors.confirmPassword} label="Confirm password" name="confirmPassword" type="password" />
        {message ? <p className="rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">{message}</p> : null}
        {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <Button className="w-full" isLoading={isSubmitting} type="submit">
          Reset password
        </Button>
        <Link className="block text-center text-sm font-medium text-[#0948B3] hover:underline" href="/login">
          Back to sign in
        </Link>
      </form>
    </AuthCard>
  );
}

