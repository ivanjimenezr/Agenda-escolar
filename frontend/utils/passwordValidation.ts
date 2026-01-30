/**
 * Password Validation Utility
 * Validates password requirements and provides real-time feedback
 */

export interface PasswordRequirement {
  id: string;
  label: string;
  regex: RegExp;
  met: boolean;
}

export interface PasswordValidation {
  requirements: PasswordRequirement[];
  isValid: boolean;
  strength: 'weak' | 'medium' | 'strong';
}

/**
 * Validate password against all requirements
 */
export function validatePassword(password: string): PasswordValidation {
  const requirements: PasswordRequirement[] = [
    {
      id: 'minLength',
      label: 'Mínimo 8 caracteres',
      regex: /.{8,}/,
      met: false
    },
    {
      id: 'uppercase',
      label: 'Una letra mayúscula (A-Z)',
      regex: /[A-Z]/,
      met: false
    },
    {
      id: 'lowercase',
      label: 'Una letra minúscula (a-z)',
      regex: /[a-z]/,
      met: false
    },
    {
      id: 'number',
      label: 'Un número (0-9)',
      regex: /[0-9]/,
      met: false
    }
  ];

  // Check each requirement
  requirements.forEach(req => {
    req.met = req.regex.test(password);
  });

  // Check if all requirements are met
  const isValid = requirements.every(req => req.met);

  // Calculate strength
  const metCount = requirements.filter(req => req.met).length;
  let strength: 'weak' | 'medium' | 'strong';

  if (metCount <= 1) {
    strength = 'weak';
  } else if (metCount <= 3) {
    strength = 'medium';
  } else {
    strength = 'strong';
  }

  return {
    requirements,
    isValid,
    strength
  };
}
