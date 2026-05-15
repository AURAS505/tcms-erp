"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { z } from "zod";
import { AuthCard } from "@/components/auth/AuthCard";
import { Button } from "@/components/ui/Button";
import { TextInput } from "@/components/ui/TextInput";
import { authService } from "@/lib/auth";

const schema = z.object({
  email: z.string().email("Enter a valid email address"),
});

export default function ForgotPasswordPage() {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setMessage("");
    setFieldError("");

    const result = schema.safeParse({ email: new FormData(event.currentTarget).get("email") });
    if (!result.success) {
      setFieldError(result.error.issues[0]?.message ?? "Email is required");
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.requestPasswordReset(result.data);
      setMessage("If the email exists, a reset link will be sent.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to request reset");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthCard subtitle="Request a password reset link for your staff account." title="Forgot your password?">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <TextInput error={fieldError} label="Email address" name="email" type="email" autoComplete="email" />
        {message ? <p className="rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">{message}</p> : null}
        {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <Button className="w-full" isLoading={isSubmitting} type="submit">
          Recover password
        </Button>
        <Link className="block text-center text-sm font-medium text-[#0948B3] hover:underline" href="/login">
          Back to sign in
        </Link>
      </form>
    </AuthCard>
  );
}

